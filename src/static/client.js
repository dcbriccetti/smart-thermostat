class Client {
  constructor() {
    this.sliceSecs = 15;
    document.getElementById('zoom').value = this.sliceSecs;
    fetch('all-status').then(r => r.json()).then(j => addAllStateRecords(j));
    const se = this.eventSource = new EventSource('/status');
    console.log(se.readyState);
    se.onopen = parm => console.log(parm, se.readyState);
    se.onmessage = event => this.processEvent(JSON.parse(event.data));
    se.onerror = error => console.error('Status events error', error, se.readyState);
  }

  processEvent(state) {
    console.log('event arrived');
    addStateRecord(state);
    const el = id => document.getElementById(id);
    el('outside-temperature').textContent = state.outside_temp.toFixed(0);
    el('temperature').textContent = state.current_temp.toFixed(1);
    el('humidity').textContent = state.current_humidity.toFixed(0);
    el('display-desired').textContent = state.desired_temp.toFixed(1);
  }

  adjustTemp(amount) {
    fetch('increase_temperature', {
      method: 'POST',
      body: amount
    }).then(response => response);
  }

  schedule() {
    fetch('schedule', {
      method: 'PUT',
      body: document.getElementById('schedule').value
    }).then(response => response);
  }

  zoom() {
    this.sliceSecs = Number(document.getElementById('zoom').value)
  }

  visibilityChanged(visible) {
    console.log(`vis changed to ${visible}. eventSource.readyState: ${this.eventSource.readyState}`);
  }
}

const client = new Client();

function handleVisibilityChange() {
  client.visibilityChanged(! document.hidden);
}

document.addEventListener("visibilitychange", handleVisibilityChange, false);
