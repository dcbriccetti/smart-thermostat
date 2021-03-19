///<reference path="thermoClient.ts"/>
declare const p5: new (arg0: (p: any) => void) => any

const thermoSketch = new p5(p => {

  let stateRecords: State[] = []

  p.setup = () => {
    const vis = <HTMLElement> document.querySelector('#visualization')
    p.createCanvas(vis.offsetWidth, vis.offsetHeight).parent('visualization')
  }

  let timeToXFn: { (time: number): number }

  function getVisibleStateRecords() {
    // Find leftmost visible record, so we can draw from left to right
    if (timeToXFn === undefined) return []  // Can’t run until draw has run once to compute the number of visible records

    let leftmost_visible_record_index = 0
    for (let i = stateRecords.length - 1; i >= 0; --i) {
      if (timeToXFn(stateRecords[i].time) < 0) {
        leftmost_visible_record_index = i
        break
      }
    }

    return stateRecords.slice(leftmost_visible_record_index)
  }

  p.draw = () => {
    p.frameRate(0.5)
    p.background('#e0e0e0')
    p.translate(0, p.height)
    p.scale(1, -1)

    if (stateRecords.length === 0) return

    let timeStart = stateRecords[0].time
    let timeEnd = p.int(Date.now() / 1000)

    let xRight = p.width - 20

    function timeToX(time: number) {
      const secondsFromEnd = timeEnd - time
      const pixelsFromEnd = secondsFromEnd / thermoClient.sliceSecs
      return xRight - pixelsFromEnd
    }

    if (timeToXFn === undefined) {
      timeToXFn = timeToX
      thermoClient.sketchIsReady()
    }

    const visibleStateRecords = getVisibleStateRecords()

    const minOrMax = (reduce_fn: any, initial_value: number) => visibleStateRecords.reduce(reduce_fn, initial_value)
    const createTempReduceFn = (minMaxFn: any) => (a: State, c: State) => {
      const temps = [a, c.inside_temp]
      if (thermoClient.showingDesiredTemp) temps.push(c.desired_temp)
      if (thermoClient.showingOutsideTemp) temps.push(c.outside_temp)
      return minMaxFn(...temps)
    }
    const y_axis_margin_degrees = 1
    const temp_min = minOrMax(createTempReduceFn(Math.min),  50) - y_axis_margin_degrees
    const temp_max = minOrMax(createTempReduceFn(Math.max), -50) + y_axis_margin_degrees
    const chartYBase = 20

    const tempToY = (temp: number) => p.map(temp, temp_min, temp_max, chartYBase, p.height)

    function drawVertGridLines() {
      const gridLow = Math.floor(temp_min)
      const gridHigh = Math.ceil(temp_max)
      const smallRange = gridHigh - gridLow < 5

      for (let gt = gridLow; gt < gridHigh; gt++) {
        const gly = tempToY(gt)
        p.strokeWeight(1)
        p.stroke(200)
        p.line(0, gly, p.width, gly)

        if (smallRange || gt % 5 === 0) {
          p.push()
          p.scale(1, -1)
          p.strokeWeight(1)
          p.textAlign(p.RIGHT, p.CENTER)
          p.textStyle(p.NORMAL)
          p.text(gt, p.width - 3, -gly)
          p.pop()
        }
      }
    }

    function drawHorzGridLines() {
      const fifteenMins = 60 * 15
      const sixtyMins = 60 * 60
      const firstLineTime = timeStart - timeStart % fifteenMins + fifteenMins

      for (let lineTime = firstLineTime; lineTime < timeEnd; lineTime += fifteenMins) {
        const lineX = timeToX(lineTime)
        const is60MinMultiple = lineTime % sixtyMins === 0
        p.strokeWeight(is60MinMultiple ? 2 : 1)
        p.stroke(128)
        p.line(lineX, chartYBase, lineX, p.height)
        if (is60MinMultiple) {
          p.push()
          p.scale(1, -1)
          p.textAlign(p.CENTER, p.BOTTOM)
          p.strokeWeight(0)
          p.text(new Date(lineTime * 1000).getHours(), lineX, 0)
          p.pop()
        }
      }
    }

    drawVertGridLines()
    drawHorzGridLines()

    for (const rec of visibleStateRecords) {
      const x = timeToX(rec.time)

      p.strokeWeight(3)

      if (thermoClient.showingDesiredTemp) {
        p.stroke('green')
        p.point(x, tempToY(rec.desired_temp))
      }

      if (thermoClient.showingOutsideTemp) {
        p.stroke(255, 190, 0)
        p.point(x, tempToY(rec.outside_temp))
      }

      p.stroke(rec.heater_is_on ? 'red' : 'black')
      p.point(x, tempToY(rec.inside_temp))
    }
  }

  p.setStateRecords = (records: State[]) => stateRecords = records

  p.getVisibleStateRecords = getVisibleStateRecords
})

const thermoClient = new ThermoClient(thermoSketch)
