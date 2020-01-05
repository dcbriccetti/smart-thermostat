'Smart thermostat project main module'

from queue import Queue
from flask import Flask, jsonify, render_template, request, Response
import json
import threading
from rpi.sensor import Sensor
from rpi.heaterrelay import HeaterRelay
from thermocontroller import ThermoController
from scheduler import Scheduler

WEATHER_STATION = 'KCCR'
TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

controller = ThermoController(WEATHER_STATION, Sensor(), HeaterRelay(), DEFAULT_DESIRED_TEMP)
scheduler = Scheduler(controller)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', weather_station=WEATHER_STATION)


@app.route('/increase_temperature', methods=('POST',))
def increase_temperature():
    controller.increase_temperature(float(request.get_data()))
    return ''


@app.route('/set_temperature', methods=('PUT',))
def set_temperature():
    controller.set_temperature(float(request.get_data()))
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
