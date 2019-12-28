'Smart thermostat project main module'

from time import sleep
from flask import Flask, render_template, jsonify, request
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


@app.route('/temperature')
def temperature():
    return jsonify(controller.current_temp)


@app.route('/desired', methods=('PUT',))
def desired():
    new_temp = float(request.get_data())
    controller.set_desired_temp(new_temp)
    return ''


def controller_thread():
    while True:
        controller.update()
        sleep(1)


threading.Thread(target=controller_thread).start()

app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
