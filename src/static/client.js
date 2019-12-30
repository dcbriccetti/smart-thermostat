class Client {
  constructor() {
    fetch('all-status').then(r => r.json()).then(j => addAllStateRecords(j));
    new EventSource('/status').onmessage = event => {
      const data = event.data;
      try {
        console.log('parsing', data);
        const json = JSON.parse(data);
        this.processEvent(json);
      } catch (e) {
        console.log(e, data);
      }
    }
  }

  processEvent(state) {
    addStateRecord(state);
    const el = (id) => document.getElementById(id);
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
