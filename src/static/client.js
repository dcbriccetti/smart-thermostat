class Client {
  constructor() {
    fetch('all-status').then(r => r.json()).then(j => addAllStateRecords(j));
    new EventSource('/status').onmessage = event => this.processEvent(JSON.parse(event.data));
  }

  processEvent(state) {
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
}

const client = new Client();
