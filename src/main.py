'Smart thermostat project main module'

import json
import threading
from datetime import datetime
from queue import Queue
from time import sleep

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
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    inside_temp = db.Column(db.Float)
    outside_temp = db.Column(db.Float)
    desired_temp = db.Column(db.Float)
    inside_humidity = db.Column(db.Float)
    outside_humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    weather_codes = db.Column(db.String)
    heater_is_on = db.Column(db.Boolean)

db.create_all()

observations = Observation.query.order_by(Observation.time).all()

controller = ThermoController(WEATHER_QUERY, Sensor(), observations,
    heater=Relay('Heat', HEAT_PIN), cooler=Relay('AC', COOL_PIN),
    fan=Relay('Fan', FAN_PIN), desired_temp=DEFAULT_DESIRED_TEMP)
scheduler = Scheduler(controller)

@app.route('/')
def index():
    return render_template(
        'index.html', weather_query=WEATHER_QUERY.split('=')[1],
        schedule=scheduler.render())


@app.route('/change_temperature', methods=('POST',))
def change_temperature():
    controller.change_temperature(float(request.get_data()))
    return ''


@app.route('/set_temperature', methods=('PUT',))
def set_temperature():
    controller.set_temperature(float(request.get_data()))
    return ''


@app.route('/activate_fan', methods=('PUT',))
def activate_fan():
    controller.activate_fan(request.get_data() == b'true')
    return ''


@app.route('/enable_cool', methods=('PUT',))
def enable_cool():
    controller.enable_cool(request.get_data() == b'true')
    return ''


@app.route('/schedule', methods=('PUT',))
def schedule():
    scheduler.set(request.get_data())
    return ''


@app.route('/status')
def status():
    stream_state_queue = Queue(maxsize=5)
    controller.add_state_queue(stream_state_queue)

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
        if state := controller.update():
            print(state)
            ob = Observation(
                time=datetime.fromtimestamp(state['time']),
                inside_temp=state['inside_temp'],
                outside_temp=state['outside_temp'],
                desired_temp=state['desired_temp'],
                inside_humidity=state['inside_humidity'],
                outside_humidity=state['outside_humidity'],
                pressure=state['pressure'],
                weather_codes=', '.join([str(mw['id']) for mw in state['main_weather']]),
                heater_is_on=state['heater_is_on']
            )
            db.session.add(ob)
            db.session.commit()
        sleep(.1)


threading.Thread(target=_background_thread).start()

app.run(host='localhost', threaded=True, debug=True, use_reloader=False)
