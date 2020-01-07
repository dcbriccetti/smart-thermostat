let stateRecords = [];

function setup() {
  const vis = $('#visualization');
  createCanvas(vis.width(), vis.height()).parent('visualization');
}

function drawGridLines(temp_min, temp_max, scy) {
  const gridLow = floor(temp_min);
  const gridHigh = ceil(temp_max);
  const smallRange = gridHigh - gridLow < 5;

  for (let gt = gridLow; gt < gridHigh; gt++) {
    const gly = scy(gt);
    strokeWeight(1);
    stroke(200);
    line(0, gly, width, gly);

    if (smallRange || gt % 5 === 0) {
      push();
      scale(1, -1);
      strokeWeight(1);
      textAlign(RIGHT, CENTER);
      textStyle(NORMAL);
      text(gt, width - 3, -gly);
      pop();
    }
  }
}

function drawXGridLine(timeStart, x, chartYBase) {
  const is15MinMultiple = timeStart % (60 * 15) === 0;
  const is60MinMultiple = is15MinMultiple && timeStart % (60 * 60) === 0;

  if (is15MinMultiple) {
    strokeWeight(is60MinMultiple ? 2 : 1);
    stroke(128);
    line(x, chartYBase, x, height);
  }

  if (is60MinMultiple) {
    push();
    scale(1, -1);
    textAlign(CENTER, BOTTOM);
    strokeWeight(0);
    text(new Date(timeStart * 1000).getHours(), x, 0);
    pop();
  }
}

function draw() {
  frameRate(0.5);
  background('#e0e0e0');
  translate(0, height);
  scale(1, -1);

  if (stateRecords.length === 0) return;

  function minOrMax(fn, iv) {
    const rf = (a, c) => fn(a, c.current_temp, c.desired_temp, c.outside_temp);
    return stateRecords.reduce(rf, iv);
  }

  const temp_min = minOrMax(Math.min, 50);
  const temp_max = minOrMax(Math.max, -50);
  const chartYBase = 20;

  let timeEnd = int(Date.now() / 1000);

  let xRight = width - 20;
  let iState = stateRecords.length - 1;

  function tempAge(rec) {
    return (rec.time - rec.outside_temp_collection_time) / 60;
  }

  console.time('drawpoints');
  const tempToY = y => map(y, temp_min, temp_max, chartYBase, height);
  drawGridLines(temp_min, temp_max, tempToY);
  for (let i = stateRecords.length - 1; i >= 0; --i) {

    const rec = stateRecords[i];
    let timeStart = timeEnd - client.sliceSecs;
    const timeToX = time => map(time, stateRecords[0].time, timeEnd, 0, xRight);

    const cty = tempToY(rec.current_temp);
    const dty = tempToY(rec.desired_temp);
    const oat = tempToY(rec.outside_temp);

    const x = timeToX(rec.time);

//      drawXGridLine(timeStart, x, chartYBase);

    strokeWeight(3);
    stroke('blue');
    point(x, cty);

    stroke('green');
    point(x, dty);

    const opacity = map(min(tempAge(rec), 60), 0, 60, 255, 0);
    stroke(0, 0, 0, 255);
    point(x, oat);

    if (rec.heater_is_on) {
      stroke('#9C2A00');
      point(x, chartYBase - 6);
    }
  }

  console.timeEnd('drawpoints');
}

function addStateRecord(state) {
  stateRecords.push(state);
}

function addAllStateRecords(records) {
  stateRecords = records;
}
