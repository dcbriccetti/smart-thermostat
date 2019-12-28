class Client {
  constructor() {
    this.updateTemperature();
  }

  updateTemperature() {
    console.log('Updating temperature');
    fetch('temperature').then((data) => {
      return data.json();
    }).then(j => {
      document.getElementById('temperature').textContent = j.toFixed(1);
      setTimeout(client.updateTemperature, 30000);
    });
  }

  setDesired(desired) {
      document.getElementById('display-desired').textContent = desired;
      fetch('desired', {
          method: 'PUT',
          body: desired
      }).then(response => {
	  console.log('Desired put response', response);
	  return response;
      });
  }
}

const client = new Client();
