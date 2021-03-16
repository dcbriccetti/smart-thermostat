'Smart thermostat project main module'

import json
import threading
from datetime import datetime
from queue import Queue
from time import sleep, time

from flask import Flask, jsonify, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy

try:
    from rpi.sensor import Sensor
    from rpi.relay import Relay
    import board
    HEAT_PIN = board.D21
    FAN_PIN  = board.D16
    COOL_PIN  = board.D12
except ModuleNotFoundError:
    from mock.sensor import Sensor
    from mock.relay import Relay
    HEAT_PIN = FAN_PIN = COOL_PIN = None
from thermocontroller import ThermoController
from scheduler import Scheduler

WEATHER_QUERY = 'zip=94549'
TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../thermostat.db'
db = SQLAlchemy(app)

class Observation(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    time                = db.Column(db.DateTime)
    inside_temp         = db.Column(db.Float)
    outside_temp        = db.Column(db.Float)
    desired_temp        = db.Column(db.Float)
    inside_humidity     = db.Column(db.Float)
    outside_humidity    = db.Column(db.Float)
    pressure            = db.Column(db.Float)
    weather_codes       = db.Column(db.String)
    heater_is_on        = db.Column(db.Boolean)

db.create_all()

t = time()
observations = Observation.query.order_by(Observation.time).all()
print(f'Past observations fetched from database in {(time() - t) * 1000:.3f} ms')

thermoController = ThermoController(WEATHER_QUERY, Sensor(), observations,
    heater=Relay('Heat', HEAT_PIN), cooler=Relay('AC', COOL_PIN),
    fan=Relay('Fan', FAN_PIN), desired_temp=DEFAULT_DESIRED_TEMP)
scheduler = Scheduler(thermoController)

@app.route('/')
def index():
    return render_template(
        'index.html', weather_query=WEATHER_QUERY.split('=')[1],
        schedule=scheduler.render())


@app.route('/change_temperature', methods=('POST',))
def change_temperature():
    thermoController.change_temperature(float(request.get_data()))
    return ''


@app.route('/set_temperature', methods=('PUT',))
def set_temperature():
    thermoController.set_temperature(float(request.get_data()))
    return ''


@app.route('/activate_fan', methods=('PUT',))
def activate_fan():
    thermoController.activate_fan(request.get_data() == b'true')
    return ''


@app.route('/enable_cool', methods=('PUT',))
def enable_cool():
    thermoController.enable_cool(request.get_data() == b'true')
    return ''


@app.route('/schedule', methods=('PUT',))
def schedule():
    scheduler.set(request.get_data())
    return ''


@app.route('/status')
def status():
    stream_state_queue = Queue(maxsize=5)
    thermoController.add_state_queue(stream_state_queue)

    def event_stream():
        while True:
            state = stream_state_queue.get()
            yield f'data: {json.dumps(state)}\n\n'

    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/all-status')
def all_status():
    return jsonify(thermoController.status_history[-3 * 60 * 24:])


def _background_thread():
    while True:
        scheduler.update()
        if state := thermoController.update():
            print(state)
            if 'outside_temp' in state:
                save_observation(state)
        sleep(.1)


def save_observation(state):
    keys = 'inside_temp outside_temp desired_temp inside_humidity outside_humidity pressure heater_is_on'.split(' ')
    args_dict = {key: state[key] for key in keys}
    ob = Observation(
        time=datetime.fromtimestamp(state['time']),
        weather_codes=', '.join([str(mw['id']) for mw in state['main_weather']]),
        **args_dict
    )
    db.session.add(ob)
    db.session.commit()


threading.Thread(target=_background_thread).start()

app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
