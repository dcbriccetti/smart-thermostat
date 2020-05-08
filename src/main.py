'Smart thermostat project main module'

from queue import Queue
from flask import Flask, jsonify, render_template, request, Response
import json
import threading
try:
    from rpi.sensor import Sensor
    from rpi.relay import Relay
    import board
    HEAT_PIN = board.D21
    FAN_PIN  = board.D12
    COOL_PIN  = board.D12
except ModuleNotFoundError:
    from mock.sensor import Sensor
    from mock.relay import Relay
    HEAT_PIN = FAN_PIN = COOL_PIN = None
from thermocontroller import ThermoController
from scheduler import Scheduler

WEATHER_STATION = 'KCCR'
TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

controller = ThermoController(WEATHER_STATION, Sensor(), heater=Relay('Heat', HEAT_PIN), fan=Relay('Fan', FAN_PIN), desired_temp=DEFAULT_DESIRED_TEMP)
scheduler = Scheduler(controller)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'index.html', weather_station=WEATHER_STATION,
        schedule=scheduler.render())


@app.route('/increase_temperature', methods=('POST',))
def increase_temperature():
    controller.increase_temperature(float(request.get_data()))
    return ''


@app.route('/set_temperature', methods=('PUT',))
def set_temperature():
    controller.set_temperature(float(request.get_data()))
    return ''


@app.route('/activate_fan', methods=('PUT',))
def activate_fan():
    controller.activate_fan(request.get_data() == b'true')
    return ''


@app.route('/schedule', methods=('PUT',))
def schedule():
    scheduler.set(request.get_data())
    return ''


@app.route('/status')
def status():
    stream_state_queue = Queue(maxsize=5)
    controller.add_listener(stream_state_queue)

    def event_stream():
        while True:
            state = stream_state_queue.get()
            yield 'data: {}\n\n'.format(json.dumps(state))

    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/all-status')
def all_status():
    return jsonify(controller.status_history)


def _background_thread():
    while True:
        scheduler.update()
        controller.update()


threading.Thread(target=_background_thread).start()

app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
