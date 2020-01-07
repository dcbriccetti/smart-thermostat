let stateRecords = [];

function setup() {
  const vis = $('#visualization');
  createCanvas(vis.width(), vis.height()).parent('visualization');
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

  let timeStart = stateRecords[0].time;
  let timeEnd = int(Date.now() / 1000);

  let xRight = width - 20;

  console.time('drawpoints');
  const tempToY = y => map(y, temp_min, temp_max, chartYBase, height);
  const timeToX = time => {
    const secondsFromEnd = timeEnd - time;
    const pixelsFromEnd = secondsFromEnd / client.sliceSecs;
    return xRight - pixelsFromEnd;
  };

  function drawVertGridLines() {
    const gridLow = floor(temp_min);
    const gridHigh = ceil(temp_max);
    const smallRange = gridHigh - gridLow < 5;

    for (let gt = gridLow; gt < gridHigh; gt++) {
      const gly = tempToY(gt);
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

  function drawHorzGridLines() {
    const fifteenMins = 60 * 15;
    const sixtyMins = 60 * 60;
    const firstLineTime = timeStart - timeStart % fifteenMins + fifteenMins;

    for (let lineTime = firstLineTime; lineTime < timeEnd; lineTime += fifteenMins) {
      const lineX = timeToX(lineTime);
      const is60MinMultiple = lineTime % sixtyMins === 0;
      strokeWeight(is60MinMultiple ? 2 : 1);
      stroke(128);
      line(lineX, chartYBase, lineX, height);
      if (is60MinMultiple) {
        push();
        scale(1, -1);
        textAlign(CENTER, BOTTOM);
        strokeWeight(0);
        text(new Date(lineTime * 1000).getHours(), lineX, 0);
        pop();
      }
    }
  }

  drawVertGridLines();
  drawHorzGridLines();

  for (let i = stateRecords.length - 1; i >= 0; --i) {
    const rec = stateRecords[i];
    const x = timeToX(rec.time);

    strokeWeight(3);
    stroke('blue');
    point(x, tempToY(rec.current_temp));

    stroke('green');
    point(x, tempToY(rec.desired_temp));

    const opacity = map(min((rec.time - rec.outside_temp_collection_time) / 60, 60), 0, 60, 255, 0);
    stroke(0, 0, 0, opacity);
    point(x, tempToY(rec.outside_temp));

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
