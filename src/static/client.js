class Client {
  constructor() {
    fetch('all-status').then(r => r.json()).then(j => addAllStateRecords(j));
    new EventSource('/status').onmessage = event => this.processEvent(JSON.parse(event.data));
  }

  processEvent(state) {
    addStateRecord(state);
    const el = id => document.getElementById(id);
    el('outside-temperature').textContent = state.outside_temp.toFixed(1);
    el('temperature').textContent = state.current_temp.toFixed(1);
    el('humidity').textContent = state.current_humidity.toFixed(1);
    el('display-desired').textContent = el('desired').value = state.desired_temp.toFixed(1);
  }

  setDesired(desired) {
    fetch('desired', {
      method: 'PUT',
      body: desired
    }).then(response => response);
  }
}

const client = new Client();
