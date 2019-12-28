'Smart thermostat project main module'

from time import sleep
from queue import Queue
from flask import Flask, render_template, request, Response
import json
import threading
from rpi.sensor import Sensor
from rpi.heaterrelay import HeaterRelay
from thermocontroller import ThermoController

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

controller = ThermoController(Sensor(), HeaterRelay(), DEFAULT_DESIRED_TEMP)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/desired', methods=('PUT',))
def desired():
    controller.set_desired_temp(float(request.get_data()))
    return ''


@app.route('/stream')
def stream():
    stream_state_queue = Queue(maxsize=5)
    controller.add_listener(stream_state_queue)

    def event_stream():
        while True:
            yield f'data: {json.dumps(stream_state_queue.get())}\n\n'

    return Response(event_stream(), mimetype="text/event-stream")


def controller_thread():
    while True:
        controller.update()
        sleep(1)


threading.Thread(target=controller_thread).start()

app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
