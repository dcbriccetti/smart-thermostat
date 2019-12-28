class Client {
  constructor() {
    this.updateTemperature();
  }

  updateTemperature() {
    console.log('Updating temperature');
    fetch('temperature').then((data) => {
      return data.json();
    }).then(j => {
      console.log(j);
      document.getElementById('temperature').textContent = j;
      setTimeout(client.updateTemperature, 2000);
    });
  }

  setDesired(desired) {
      document.getElementById('display-desired').textContent = desired;
      fetch('desired', {
          method: 'PUT',
          body: desired
      });
  }
}

const client = new Client();
