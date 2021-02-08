interface Sketch {
  setStateRecords: ([]) => void
}

interface State {
  inside_temp:      number
  desired_temp:     number
  outside_temp:     number
  wind_dir:         number
  wind_speed:       number
  gust:             number
  pressure:         number
  main_weather:     [{
    icon: string
    description: string
  }]
  inside_humidity:  number
  outside_humidity: number
}

class ThermoClient {
  public sliceSecs: number
  public showingDesiredTemp = true
  public showingOutsideTemp = true
  private eventSource: EventSource
  private stateRecords = [] // Shared with sketch.ts

  constructor(private sketch: Sketch) {
    this.sliceSecs = 15
    this.inputElement('zoom').value = this.sliceSecs.toString()
    this.setUpEventProcessing()
    document.addEventListener("visibilitychange", () => this.visibilityChanged(!document.hidden), false)
  }

  private setUpEventProcessing() {
    fetch('all-status').then(response => response.json()).then((stateRecords: [{}]) => {
      this.stateRecords = stateRecords
      this.sketch.setStateRecords(stateRecords)
    })
    const source = this.eventSource = new EventSource('/status')
    console.log(`Created EventSource. readyState: ${source.readyState}`)
    source.onopen    = parm  => console.log(parm, source.readyState)
    source.onmessage = event => this.processEvent(JSON.parse(event.data))
    source.onerror   = error => console.error('Status events error', error, source.readyState)
  }

  private processEvent(state: State) {
    console.log('event arrived')
    this.stateRecords.push(state)
    const set = (id: string, text: any) => document.getElementById(id).textContent = text
    const sset = (id: string, decimalPlaces: number) => set(id, state[id].toFixed(decimalPlaces))

    sset('outside_temp',     1)
    sset('wind_dir',         0)
    sset('wind_speed',       0)
    sset('inside_temp',      1)
    sset('pressure',         0)
    sset('inside_humidity',  0)
    sset('outside_humidity', 0)
    sset('desired_temp',     1)

    set('gust', state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`)
    set('outside_temp_change_slope', this.outside_temp_change_slope().toFixed(3))
    set('inside_temp_change_slope', this.inside_temp_change_slope().toFixed(3))

    const mwElem = document.getElementById('main_weather')
    mwElem.innerHTML = ''
    state.main_weather.forEach(mw => {
      const img = document.createElement('img')
      img.src = `http://openweathermap.org/img/wn/${mw.icon}.png`
      img.alt = img.title = mw.description
      img.classList.add('weather-img')
      mwElem.appendChild(img)
    });
  }

  adjustTemp(amount: number) {
    fetch('change_temperature', {
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
      body: this.inputElement('schedule').value
    }).then(response => response)
  }

  showDesiredTemp(show: boolean) {
    this.showingDesiredTemp = show
  }

  showOutsideTemp(show: boolean) {
    this.showingOutsideTemp = show
  }

  private zoom() {
    this.sliceSecs = Number(this.inputElement('zoom').value)
  }

  private visibilityChanged(visible) {
    const rs = this.eventSource.readyState
    console.log(`vis changed to ${visible}. eventSource.readyState: ${rs}`)
    if (visible && rs === 2 /* closed */) {
      this.setUpEventProcessing()
    }
  }

  private inputElement(selector: string) {
    return <HTMLInputElement>document.getElementById(selector)
  }

  private inside_temp_change_slope(): number {
    return this.temp_change_slope(state => state.inside_temp)
  }

  private outside_temp_change_slope(): number {
    return this.temp_change_slope(state => state.outside_temp)
  }

  private temp_change_slope(fieldFromState: (state) => number): number {
    const n = this.stateRecords.length
    if (n < 2) return 0
    const numRecentElements = Math.min(30, n)

    const firstState = this.stateRecords[n - numRecentElements]
    const firstTime = firstState.time
    const firstTemp = fieldFromState(firstState)
    const recentStates = this.stateRecords.slice(n - numRecentElements, n)
    const xs = recentStates.map(state => (state.time - firstTime) / 3600)
    const ys = recentStates.map(state => fieldFromState(state) - firstTemp)
    return ThermoClient.slope(ys, xs)
  }

  private static slope(ys, xs) {
    const n = ys.length
    let sum_x = 0
    let sum_y = 0
    let sum_xy = 0
    let sum_xx = 0
    let sum_yy = 0

    for (var i = 0; i < ys.length; i++) {
      const x = xs[i]
      const y = ys[i]
      sum_x += x
      sum_y += y
      sum_xy += x * y
      sum_xx += x * x
      sum_yy += y * y
    }

    return (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
  }
}
