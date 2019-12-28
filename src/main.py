'Smart thermostat project main module'

from time import sleep
from flask import Flask, render_template, jsonify, request
import threading
from mock.sensor import Sensor
from mock.heaterrelay import HeaterRelay
from thermocontroller import ThermoController

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

app = Flask(__name__)
controller = ThermoController(Sensor(), HeaterRelay(), DEFAULT_DESIRED_TEMP)


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
    print('desired', new_temp)
    return 'OK'


def controller_thread():
    while True:
        controller.update()
        sleep(1)


threading.Thread(target=controller_thread).start()

app.run(threaded=True, debug=True)
