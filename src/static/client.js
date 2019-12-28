class Client {
  constructor() {
    const source = new EventSource('/stream');
    source.onmessage = event => {
      console.log(event);
      this.setUi(JSON.parse(event.data));
    };
  }

  setUi(state) {
    document.getElementById('temperature').textContent = state.current_temp.toFixed(1);
    document.getElementById('humidity').textContent = state.current_humidity.toFixed(1);
    document.getElementById('display-desired').textContent =
      document.getElementById('desired').value = state.desired_temp.toFixed(1);
  }

  setDesired(desired) {
    fetch('desired', {
      method: 'PUT',
      body: desired
    }).then(response => response);
  }
}

const client = new Client();
