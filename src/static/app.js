class ThermoClient {
    constructor(sketch) {
        this.sketch = sketch;
        this.showingDesiredTemp = true;
        this.showingOutsideTemp = true;
        this.stateRecords = []; // Shared with sketch.ts
        this.sliceSecs = 15;
        this.inputElement('zoom').value = this.sliceSecs.toString();
        this.setUpEventProcessing();
        document.addEventListener("visibilitychange", () => this.visibilityChanged(!document.hidden), false);
        document.querySelector('#show-desired-temp').addEventListener('change', (e) => thermoClient.showDesiredTemp(e.target.checked));
        document.querySelector('#show-outside-temp').addEventListener('change', (e) => thermoClient.showOutsideTemp(e.target.checked));
    }
    setUpEventProcessing() {
        fetch('all-status').then(response => response.json()).then((stateRecords) => {
            this.stateRecords = stateRecords;
            this.sketch.setStateRecords(stateRecords);
            const source = this.eventSource = new EventSource('/status');
            console.log(`Created EventSource. readyState: ${source.readyState}`);
            source.onopen = parm => console.log(parm, source.readyState);
            source.onmessage = event => {
                const state = JSON.parse(event.data);
                this.stateRecords.push(state);
                this.processEvent(state);
            };
            source.onerror = error => console.error('Status events error', error, source.readyState);
        });
    }
    processEvent(state) {
        console.log('processEvent');
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
        this.calculateAndShowHeaterOnValues();
        set('gust', state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`);
        const arrow = (value, decimals) => (value < 0 ? '↓' : '↑') + Math.abs(value).toFixed(decimals);
        set('outside_temp_change_slope', arrow(this.change_slope(state => state.outside_temp, 30), 1));
        set('inside_temp_change_slope', arrow(this.inside_temp_change_slope(), 1));
        set('pressure_change_slope', arrow(this.change_slope(state => state.pressure, 6 * 60), 2));
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
    calculateAndShowHeaterOnValues() {
        const visibleStateRecords = this.sketch.getVisibleStateRecords();
        const numVis = visibleStateRecords.length;
        const minutesDiff = (start, end) => (visibleStateRecords[end].time - visibleStateRecords[start].time) / 60;
        let onMinutes = 0;
        let onPercent = 0;
        if (numVis >= 2) {
            for (let i = 1; i < numVis; i++)
                if (visibleStateRecords[i - 1].heater_is_on)
                    onMinutes += minutesDiff(i - 1, i);
            const visibleMinutes = minutesDiff(0, numVis - 1);
            onPercent = onMinutes / visibleMinutes * 100;
        }
        document.getElementById("power_on_percent").textContent = onPercent.toFixed(1);
        document.getElementById("power_on_minutes").textContent = onMinutes.toFixed(0);
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
            body: this.inputElement('schedule').value
        }).then(response => response);
    }
    showDesiredTemp(show) {
        this.showingDesiredTemp = show;
    }
    showOutsideTemp(show) {
        this.showingOutsideTemp = show;
    }
    zoom() {
        this.sliceSecs = Number(this.inputElement('zoom').value);
        this.calculateAndShowHeaterOnValues();
    }
    visibilityChanged(visible) {
        const rs = this.eventSource.readyState;
        console.log(`vis changed to ${visible}. eventSource.readyState: ${rs}`);
        if (visible && rs === 2 /* closed */) {
            this.setUpEventProcessing();
        }
    }
    inputElement(selector) {
        return document.getElementById(selector);
    }
    inside_temp_change_slope() {
        const numRecords = this.stateRecords.length;
        if (numRecords < 2)
            return 0;
        const numRecentRecords = Math.min(30, numRecords);
        let rightmostHeatOn = undefined; // distance from the rightmost sample
        for (let i = 0; i < numRecentRecords; ++i) {
            if (this.stateRecords[numRecords - 1 - i].heater_is_on) {
                rightmostHeatOn = i;
                break;
            }
        }
        const marginForHeatAndThermometerDelay = 5;
        let numRequested = rightmostHeatOn === undefined ? numRecentRecords :
            Math.max(3, rightmostHeatOn - marginForHeatAndThermometerDelay);
        console.log(`Using ${numRequested} samples for indoor temperature change slope calculation`);
        return this.change_slope(state => state.inside_temp, numRequested);
    }
    change_slope(fieldFromState, numRecordsInSlope) {
        const numRecords = this.stateRecords.length;
        const numRecentRecords = Math.min(numRecordsInSlope, numRecords);
        if (numRecentRecords < 2)
            return 0;
        const firstState = this.stateRecords[numRecords - numRecentRecords];
        const firstTime = firstState.time;
        const firstValue = fieldFromState(firstState);
        const recentStates = this.stateRecords.slice(numRecords - numRecentRecords, numRecords);
        const xs = recentStates.map(state => (state.time - firstTime) / 3600);
        const ys = recentStates.map(state => fieldFromState(state) - firstValue);
        return slope(ys, xs);
    }
    sketchIsReady() {
        this.calculateAndShowHeaterOnValues();
    }
}
///<reference path="thermoClient.ts"/>
const thermoSketch = new p5(p => {
    let stateRecords = [];
    p.setup = () => {
        const vis = document.querySelector('#visualization');
        p.createCanvas(vis.offsetWidth, vis.offsetHeight).parent('visualization');
    };
    let timeToXFn;
    function getVisibleStateRecords() {
        // Find leftmost visible record, so we can draw from left to right
        if (timeToXFn === undefined)
            return []; // Can’t run until draw has run once to compute the number of visible records
        let leftmost_visible_record_index = 0;
        for (let i = stateRecords.length - 1; i >= 0; --i) {
            if (timeToXFn(stateRecords[i].time) < 0) {
                leftmost_visible_record_index = i;
                break;
            }
        }
        return stateRecords.slice(leftmost_visible_record_index);
    }
    p.draw = () => {
        p.frameRate(0.5);
        p.background('#e0e0e0');
        p.translate(0, p.height);
        p.scale(1, -1);
        if (stateRecords.length === 0)
            return;
        let timeStart = stateRecords[0].time;
        let timeEnd = p.int(Date.now() / 1000);
        let xRight = p.width - 20;
        function timeToX(time) {
            const secondsFromEnd = timeEnd - time;
            const pixelsFromEnd = secondsFromEnd / thermoClient.sliceSecs;
            return xRight - pixelsFromEnd;
        }
        if (timeToXFn === undefined) {
            timeToXFn = timeToX;
            thermoClient.sketchIsReady();
        }
        const visibleStateRecords = getVisibleStateRecords();
        const minOrMax = (reduce_fn, initial_value) => visibleStateRecords.reduce(reduce_fn, initial_value);
        const createTempReduceFn = (minMaxFn) => (a, c) => {
            const temps = [a, c.inside_temp];
            if (thermoClient.showingDesiredTemp)
                temps.push(c.desired_temp);
            if (thermoClient.showingOutsideTemp)
                temps.push(c.outside_temp);
            return minMaxFn(...temps);
        };
        const y_axis_margin_degrees = 1;
        const temp_min = minOrMax(createTempReduceFn(Math.min), 50) - y_axis_margin_degrees;
        const temp_max = minOrMax(createTempReduceFn(Math.max), -50) + y_axis_margin_degrees;
        const chartYBase = 20;
        const tempToY = (temp) => p.map(temp, temp_min, temp_max, chartYBase, p.height);
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
        for (const rec of visibleStateRecords) {
            const x = timeToX(rec.time);
            p.strokeWeight(3);
            if (thermoClient.showingDesiredTemp) {
                p.stroke('green');
                p.point(x, tempToY(rec.desired_temp));
            }
            if (thermoClient.showingOutsideTemp) {
                p.stroke(255, 190, 0);
                p.point(x, tempToY(rec.outside_temp));
            }
            p.stroke(rec.heater_is_on ? 'red' : 'black');
            p.point(x, tempToY(rec.inside_temp));
        }
    };
    p.setStateRecords = (records) => stateRecords = records;
    p.getVisibleStateRecords = getVisibleStateRecords;
});
const thermoClient = new ThermoClient(thermoSketch);
function slope(ys, xs) {
    const n = ys.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumXX = 0;
    let sumYY = 0;
    for (let i = 0; i < n; i++) {
        const x = xs[i];
        const y = ys[i];
        sumX += x;
        sumY += y;
        sumXY += x * y;
        sumXX += x * x;
        sumYY += y * y;
    }
    return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
}
//# sourceMappingURL=app.js.map