interface Sketch {
  setStateRecords: ([]) => void
  getVisibleStateRecords: () => [State]
}

interface State {
  time:             number
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
  heater_is_on:     boolean
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

      const source = this.eventSource = new EventSource('/status')
      console.log(`Created EventSource. readyState: ${source.readyState}`)
      source.onopen    = parm  => console.log(parm, source.readyState)
      source.onmessage = event => {
        const state = JSON.parse(event.data)
        this.stateRecords.push(state)
        this.processEvent(state)
      }
      source.onerror   = error => console.error('Status events error', error, source.readyState)
    })
  }

  private processEvent(state: State) {
    console.log('processEvent')
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

    this.calculateAndShowHeaterOnValues()

    set('gust', state.gust == 0 ? '' : ` (g. ${state.gust.toFixed(0)})`)

    const arrow = (value: number, decimals: number) => (value < 0 ? '↓' : '↑') + Math.abs(value).toFixed(decimals)
    set('outside_temp_change_slope', arrow(this.change_slope(state => state.outside_temp, 30), 1))
    set('inside_temp_change_slope', arrow(this.inside_temp_change_slope(), 1))
    set('pressure_change_slope', arrow(this.change_slope(state => state.pressure, 6 * 60), 2))

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

  private calculateAndShowHeaterOnValues() {
    const visibleStateRecords = this.sketch.getVisibleStateRecords()
    const numVis = visibleStateRecords.length
    const minutesDiff = (start, end) => (visibleStateRecords[end].time - visibleStateRecords[start].time) / 60
    let onMinutes = 0
    let onPercent = 0
    if (numVis >= 2) {
      for (let i = 1; i < numVis; i++)
        if (visibleStateRecords[i - 1].heater_is_on)
          onMinutes += minutesDiff(i - 1, i)

      const visibleMinutes = minutesDiff(0, numVis - 1)
      onPercent = onMinutes / visibleMinutes * 100
    }
    document.getElementById("power_on_percent").textContent = onPercent.toFixed(1)
    document.getElementById("power_on_minutes").textContent = onMinutes.toFixed(0)
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

  zoom() {
    this.sliceSecs = Number(this.inputElement('zoom').value)
    this.calculateAndShowHeaterOnValues()
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
    const numRecords = this.stateRecords.length
    if (numRecords < 2) return 0

    const numRecentRecords = Math.min(30, numRecords)
    let rightmostHeatOn: number // distance from the rightmost sample
    for (let i = 0; i < numRecentRecords; ++i) {
      if (this.stateRecords[numRecords - 1 - i].heater_is_on) {
        rightmostHeatOn = i
        break
      }
    }
    const marginForHeatAndThermometerDelay = 5
    let numRequested = rightmostHeatOn === undefined ? numRecentRecords :
      Math.max(3, rightmostHeatOn - marginForHeatAndThermometerDelay)
    console.log(`Using ${numRequested} samples for indoor temperature change slope calculation`)
    return this.change_slope(state => state.inside_temp, numRequested)
  }

  private change_slope(fieldFromState: (state) => number, numRecordsInSlope: number): number {
    const numRecords = this.stateRecords.length
    const numRecentRecords = Math.min(numRecordsInSlope, numRecords)
    if (numRecentRecords < 2) return 0

    const firstState = this.stateRecords[numRecords - numRecentRecords]
    const firstTime = firstState.time
    const firstValue = fieldFromState(firstState)
    const recentStates = this.stateRecords.slice(numRecords - numRecentRecords, numRecords)
    const xs = recentStates.map(state => (state.time - firstTime) / 3600)
    const ys = recentStates.map(state => fieldFromState(state) - firstValue)
    return slope(ys, xs)
  }

  sketchIsReady() {
    this.calculateAndShowHeaterOnValues()
  }
}
