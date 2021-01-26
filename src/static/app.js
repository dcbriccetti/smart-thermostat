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
        const se = this.eventSource = new EventSource('/status');
        console.log(`Created EventSource. readyState: ${se.readyState}`);
        se.onopen = parm => console.log(parm, se.readyState);
        se.onmessage = event => this.processEvent(JSON.parse(event.data));
        se.onerror = error => console.error('Status events error', error, se.readyState);
    }
    processEvent(state) {
        console.log('event arrived');
        this.sketch.addStateRecord(state);
        const el = id => document.getElementById(id);
        el('outside-temperature').textContent = state.outside_temp.toFixed(1);
        el('wind-dir').textContent = state.wind_dir.toFixed(0);
        el('wind-speed').textContent = state.wind_speed.toFixed(0);
        el('gust').textContent = state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`;
        el('temperature').textContent = state.current_temp.toFixed(1);
        el('pressure').textContent = state.pressure.toFixed(0);
        el('humidity').textContent = state.humidity.toFixed(0);
        el('outside-humidity').textContent = state.outside_humidity.toFixed(0);
        el('main-weather').textContent = state.main_weather;
        el('display-desired').textContent = state.desired_temp.toFixed(1);
    }
    adjustTemp(amount) {
        fetch('increase_temperature', {
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
        const vis = $('#visualization');
        p.createCanvas(vis.width(), vis.height()).parent('visualization');
    };
    p.draw = () => {
        p.frameRate(0.5);
        p.background('#e0e0e0');
        p.translate(0, p.height);
        p.scale(1, -1);
        if (stateRecords.length === 0)
            return;
        function minOrMax(fn, iv) {
            const rf = (a, c) => fn(a, c.current_temp, c.desired_temp, c.outside_temp);
            return stateRecords.reduce(rf, iv);
        }
        const y_axis_margin_degrees = 1;
        const temp_min = minOrMax(Math.min, 50) - y_axis_margin_degrees;
        const temp_max = minOrMax(Math.max, -50) + y_axis_margin_degrees;
        const chartYBase = 20;
        let timeStart = stateRecords[0].time;
        let timeEnd = p.int(Date.now() / 1000);
        let xRight = p.width - 20;
        const tempToY = y => p.map(y, temp_min, temp_max, chartYBase, p.height);
        const timeToX = time => {
            const secondsFromEnd = timeEnd - time;
            const pixelsFromEnd = secondsFromEnd / thermoClient.sliceSecs;
            return xRight - pixelsFromEnd;
        };
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
        for (let i = stateRecords.length - 1; i >= 0; --i) {
            const rec = stateRecords[i];
            const x = timeToX(rec.time);
            if (x < 0)
                break;
            const prevRec = i >= 1 ? stateRecords[i - 1] : null;
            const prevX = prevRec ? timeToX(prevRec.time) : null;
            p.strokeWeight(3);
            p.stroke('blue');
            if (prevRec) {
                const prevTempY = tempToY(prevRec.current_temp);
                p.line(x, prevTempY, prevX, prevTempY);
            }
            p.point(x, tempToY(rec.current_temp));
            p.stroke('green');
            const desiredTempY = tempToY(rec.desired_temp);
            if (prevRec && prevRec.desired_temp === rec.desired_temp) {
                const prevX = timeToX(prevRec.time);
                p.line(x, desiredTempY, prevX, desiredTempY);
            }
            else
                p.point(x, desiredTempY);
            p.strokeWeight(10);
            p.stroke(255, 190, 0);
            p.point(timeToX(rec.outside_temp_collection_time), tempToY(rec.outside_temp));
            p.strokeWeight(3);
            if (rec.heater_is_on) {
                p.stroke('#9C2A00');
                p.point(x, chartYBase - 6);
            }
        }
    };
    p.addStateRecord = (state) => {
        stateRecords.push(state);
    };
    p.addAllStateRecords = (records) => {
        stateRecords = records;
    };
});
const thermoClient = new ThermoClient(thermoSketch);
//# sourceMappingURL=app.js.map