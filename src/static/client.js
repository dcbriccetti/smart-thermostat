class Client {
  constructor() {
    new EventSource('/status').onmessage = event => this.setUi(JSON.parse(event.data));
  }

  setUi(state) {
    addVizState(state);
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
