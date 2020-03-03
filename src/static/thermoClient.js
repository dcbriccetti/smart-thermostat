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
        el('outside-temperature').textContent = state.outside_temp.toFixed(0);
        el('temperature').textContent = state.current_temp.toFixed(1);
        el('humidity').textContent = state.current_humidity.toFixed(0);
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
//# sourceMappingURL=thermoClient.js.map