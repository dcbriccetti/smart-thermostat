class ThermoClient {
    constructor(sketch) {
        this.sketch = sketch;
        this.sliceSecs = 15;
        this.inEl('zoom').value = this.sliceSecs.toString();
        this.setUpEventProcessing();
        document.addEventListener("visibilitychange", () => {
            this.visibilityChanged(!document.hidden);
        }, false);
    }
    setUpEventProcessing() {
        fetch('all-status').then(r => r.json()).then(j => this.sketch.addAllStateRecords(j));
        const source = this.eventSource = new EventSource('/status');
        console.log(`Created EventSource. readyState: ${source.readyState}`);
        source.onopen = parm => console.log(parm, source.readyState);
        source.onmessage = event => this.processEvent(JSON.parse(event.data));
        source.onerror = error => console.error('Status events error', error, source.readyState);
    }
    processEvent(state) {
        console.log('event arrived');
        this.sketch.addStateRecord(state);
        const set = (id, text) => document.getElementById(id).textContent = text;
        const sset = (id, decimalPlaces) => set(id, state[id].toFixed(decimalPlaces));
        sset('outside_temp', 1);
        sset('wind_dir', 0);
        sset('wind_speed', 0);
        sset('inside_temp', 1);
        sset('pressure', 0);
        sset('inside_humidity', 0);
        sset('outside_humidity', 0);
        sset('desired_temp', 1);
        set('gust', state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`);
        const mwElem = document.getElementById('main_weather');
        mwElem.innerHTML = '';
        state.main_weather.forEach(mw => {
            const img = document.createElement('img');
            img.src = `http://openweathermap.org/img/wn/${mw.icon}.png`;
            img.alt = img.title = mw.description;
            img.classList.add('weather-img');
            mwElem.appendChild(img);
        });
    }
    adjustTemp(amount) {
        fetch('change_temperature', {
            method: 'POST',
            body: amount.toString()
        }).then(response => response);
    }
    activateFan(activate) {
        fetch('activate_fan', {
            method: 'PUT',
            body: activate
        }).then(response => response);
    }
    enableCool(enable) {
        fetch('enable_cool', {
            method: 'PUT',
            body: enable
        }).then(response => response);
    }
    schedule() {
        fetch('schedule', {
            method: 'PUT',
            body: this.inEl('schedule').value
        }).then(response => response);
    }
    zoom() {
        this.sliceSecs = Number(this.inEl('zoom').value);
    }
    visibilityChanged(visible) {
        const rs = this.eventSource.readyState;
        console.log(`vis changed to ${visible}. eventSource.readyState: ${rs}`);
        if (visible && rs === 2 /* closed */) {
            this.setUpEventProcessing();
        }
    }
    inEl(selector) {
        return document.getElementById(selector);
    }
}
///<reference path="thermoClient.ts"/>
const thermoSketch = new p5(p => {
    let stateRecords = [];
    p.setup = () => {
        const vis = document.querySelector('#visualization');
        p.createCanvas(vis.offsetWidth, vis.offsetHeight).parent('visualization');
    };
    p.draw = () => {
        p.frameRate(0.5);
        p.background('#e0e0e0');
        p.translate(0, p.height);
        p.scale(1, -1);
        if (stateRecords.length === 0)
            return;
        const minOrMax = (reduce_fn, initial_value) => stateRecords.reduce(reduce_fn, initial_value);
        const createTempReduceFn = minMaxFn => (a, c) => minMaxFn(a, c.inside_temp, c.desired_temp, c.outside_temp);
        const createPressureReduceFn = minMaxFn => (a, c) => minMaxFn(a, c.pressure);
        const y_axis_margin_degrees = 1;
        const y_axis_margin_hPa = 10;
        const temp_min = minOrMax(createTempReduceFn(Math.min), 50) - y_axis_margin_degrees;
        const temp_max = minOrMax(createTempReduceFn(Math.max), -50) + y_axis_margin_degrees;
        const pressure_min = minOrMax(createPressureReduceFn(Math.min), 1500) - y_axis_margin_hPa;
        const pressure_max = minOrMax(createPressureReduceFn(Math.max), 0) + y_axis_margin_hPa;
        const chartYBase = 20;
        let timeStart = stateRecords[0].time;
        let timeEnd = p.int(Date.now() / 1000);
        let xRight = p.width - 20;
        const tempToY = temp => p.map(temp, temp_min, temp_max, chartYBase, p.height);
        const pressureToY = pressure => p.map(pressure, pressure_min, pressure_max, chartYBase, p.height);
        function timeToX(time) {
            const secondsFromEnd = timeEnd - time;
            const pixelsFromEnd = secondsFromEnd / thermoClient.sliceSecs;
            return xRight - pixelsFromEnd;
        }
        function drawVertGridLines() {
            const gridLow = Math.floor(temp_min);
            const gridHigh = Math.ceil(temp_max);
            const smallRange = gridHigh - gridLow < 5;
            for (let gt = gridLow; gt < gridHigh; gt++) {
                const gly = tempToY(gt);
                p.strokeWeight(1);
                p.stroke(200);
                p.line(0, gly, p.width, gly);
                if (smallRange || gt % 5 === 0) {
                    p.push();
                    p.scale(1, -1);
                    p.strokeWeight(1);
                    p.textAlign(p.RIGHT, p.CENTER);
                    p.textStyle(p.NORMAL);
                    p.text(gt, p.width - 3, -gly);
                    p.pop();
                }
            }
        }
        function drawHorzGridLines() {
            const fifteenMins = 60 * 15;
            const sixtyMins = 60 * 60;
            const firstLineTime = timeStart - timeStart % fifteenMins + fifteenMins;
            for (let lineTime = firstLineTime; lineTime < timeEnd; lineTime += fifteenMins) {
                const lineX = timeToX(lineTime);
                const is60MinMultiple = lineTime % sixtyMins === 0;
                p.strokeWeight(is60MinMultiple ? 2 : 1);
                p.stroke(128);
                p.line(lineX, chartYBase, lineX, p.height);
                if (is60MinMultiple) {
                    p.push();
                    p.scale(1, -1);
                    p.textAlign(p.CENTER, p.BOTTOM);
                    p.strokeWeight(0);
                    p.text(new Date(lineTime * 1000).getHours(), lineX, 0);
                    p.pop();
                }
            }
        }
        drawVertGridLines();
        drawHorzGridLines();
        // Find leftmost visible record, so we can draw from left to right
        let leftmost_visible_record_index = 0;
        for (let i = stateRecords.length - 1; i >= 0; --i) {
            if (timeToX(stateRecords[i].time) < 0) {
                leftmost_visible_record_index = i;
                break;
            }
        }
        for (const rec of stateRecords.slice(leftmost_visible_record_index)) {
            const x = timeToX(rec.time);
            p.strokeWeight(3);
            p.stroke('green');
            p.point(x, tempToY(rec.desired_temp));
            p.stroke('blue');
            p.point(x, pressureToY(rec.pressure));
            p.stroke(255, 190, 0);
            p.point(x, tempToY(rec.outside_temp));
            p.stroke(rec.heater_is_on ? 'red' : 'black');
            p.point(x, tempToY(rec.inside_temp));
        }
    };
    p.addStateRecord = record => stateRecords.push(record);
    p.addAllStateRecords = records => stateRecords = records;
});
const thermoClient = new ThermoClient(thermoSketch);
//# sourceMappingURL=app.js.map