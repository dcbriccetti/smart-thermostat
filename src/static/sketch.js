let stateRecords = [];

function setup() {
  const vis = $('#visualization');
  createCanvas(vis.width(), vis.height()).parent('visualization');
}

function draw() {
  frameRate(2);
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

  let timeEnd = int(Date.now() / 1000 / client.sliceSecs) * client.sliceSecs;
  const elapsed = timeEnd - stateRecords[0].time;
  const numSlices = min(width - 10, int(elapsed / client.sliceSecs));

  let x = width - 20;
  let iState = stateRecords.length - 1;

  function tempAge(rec) {
    return (rec.time - rec.outside_temp_collection_time) / 60;
  }

  for (let i = 0; i < numSlices; ++i) {
    let timeStart = timeEnd - client.sliceSecs;
    let sumTemps = 0;
    let sumDTemps = 0;
    let sumOATemps = 0;
    let sumOATempAges = 0;
    let numInPeriod = 0;
    let heatOnInPeriod = false;

    while (stateRecords[iState].time <= timeEnd && stateRecords[iState].time > timeStart) {
      const rec = stateRecords[iState];
      ++numInPeriod;
      sumTemps += rec.current_temp;
      sumDTemps += rec.desired_temp;
      sumOATemps += rec.outside_temp;
      sumOATempAges += tempAge(rec);
      if (rec.heater_is_on)
        heatOnInPeriod = true;
      --iState;
    }

    if (numInPeriod > 0 || iState > 0) {
      const prevRec = stateRecords[iState - 1];
      const avgTemp = numInPeriod > 0 ? sumTemps / numInPeriod : prevRec.current_temp;
      const avgDTemp = numInPeriod > 0 ? sumDTemps / numInPeriod : prevRec.desired_temp;
      const avgOATemp = numInPeriod > 0 ? sumOATemps / numInPeriod : prevRec.outside_temp;
      const avgOATempAges = numInPeriod > 0 ? sumOATempAges / numInPeriod : tempAge(prevRec);
      const scy = y => map(y, temp_min, temp_max, chartYBase, height);
      const cty = scy(avgTemp);
      const dty = scy(avgDTemp);
      const oat = scy(avgOATemp);

      const gridLow = floor(temp_min);
      const gridHigh = ceil(temp_max);
      for (let gt = gridLow; gt < gridHigh; gt++) {
        const gly = scy(gt);
        strokeWeight(1);
        stroke(200);
        line(0, gly, width, gly);
        push();
        scale(1, -1);
        strokeWeight(1);
        textAlign(RIGHT, CENTER);
        textStyle(NORMAL);
        text(gt, width - 3, -gly);
        pop();
      }

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

      strokeWeight(3);
      stroke('blue');
      point(x, cty);

      stroke('green');
      point(x, dty);

      const opacity = map(min(avgOATempAges, 60), 0, 60, 255, 0);
      stroke(0, 0, 0, opacity);
      point(x, oat);

      if (heatOnInPeriod) {
        stroke('#9C2A00');
        point(x, chartYBase - 6);
      }
    }

    --x;
    timeEnd -= client.sliceSecs;
  }
}

function addStateRecord(state) {
  stateRecords.push(state);
}

function addAllStateRecords(records) {
  stateRecords = records;
}
