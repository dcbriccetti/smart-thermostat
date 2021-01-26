interface Sketch {
  addAllStateRecords: (string) => void
  addStateRecord:     (string) => void
}

interface State {
  current_temp:     number
  desired_temp:     number
  outside_temp:     number
  wind_dir:         number
  wind_speed:       number
  gust:             number
  pressure:         number
  main_weather:     string
  humidity:         number
  outside_humidity: number
}

class ThermoClient {
  public sliceSecs: number
  private eventSource: EventSource

  constructor(private sketch: Sketch) {
    this.sliceSecs = 15
    this.inEl('zoom').value = this.sliceSecs.toString()
    this.setUpEventProcessing()
    document.addEventListener("visibilitychange", () => {
      this.visibilityChanged(!document.hidden)
    }, false)
  }

  setUpEventProcessing() {
    fetch('all-status').then(r => r.json()).then(j => this.sketch.addAllStateRecords(j))
    const se = this.eventSource = new EventSource('/status')
    console.log(`Created EventSource. readyState: ${se.readyState}`)
    se.onopen = parm => console.log(parm, se.readyState)
    se.onmessage = event => this.processEvent(JSON.parse(event.data))
    se.onerror = error => console.error('Status events error', error, se.readyState)
  }

  processEvent(state: State) {
    console.log('event arrived')
    this.sketch.addStateRecord(state)
    const el = id => document.getElementById(id)
    el('outside-temperature').textContent = state.outside_temp.toFixed(1)
    el('wind-dir')           .textContent = state.wind_dir.toFixed(0)
    el('wind-speed')         .textContent = state.wind_speed.toFixed(0)
    el('gust')               .textContent = state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`
    el('temperature')        .textContent = state.current_temp.toFixed(1)
    el('pressure')           .textContent = state.pressure.toFixed(0)
    el('humidity')           .textContent = state.humidity.toFixed(0)
    el('outside-humidity')   .textContent = state.outside_humidity.toFixed(0)
    el('main-weather')       .textContent = state.main_weather
    el('display-desired')    .textContent = state.desired_temp.toFixed(1)
  }

  adjustTemp(amount: number) {
    fetch('increase_temperature', {
      method: 'POST',
      body: amount.toString()
    }).then(response => response)
  }

  activateFan(activate: string) {
    fetch('activate_fan', {
      method: 'PUT',
      body: activate
    }).then(response => response)
  }

  enableCool(enable: string) {
    fetch('enable_cool', {
      method: 'PUT',
      body: enable
    }).then(response => response)
  }

  schedule() {
    fetch('schedule', {
      method: 'PUT',
      body: this.inEl('schedule').value
    }).then(response => response)
  }

  zoom() {
    this.sliceSecs = Number(this.inEl('zoom').value)
  }

  visibilityChanged(visible) {
    const rs = this.eventSource.readyState
    console.log(`vis changed to ${visible}. eventSource.readyState: ${rs}`)
    if (visible && rs === 2 /* closed */) {
      this.setUpEventProcessing()
    }
  }

  inEl(selector: string) {
    return <HTMLInputElement>document.getElementById(selector)
  }
}
