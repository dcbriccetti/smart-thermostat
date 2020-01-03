let stateRecords = [];

function setup() {
    const vis = $("#visualization");
    createCanvas(vis.width(), vis.height()).parent("visualization");
}

function draw() {
    frameRate(1);
    background('#e0e0e0');
    translate(0, height);
    scale(1, -1);
    const expanded = expand(stateRecords);
    const xoff = max(0, expanded.length - width);
    function minOrMax(fn, iv) {
        const rf = (a, c) => fn(a, c.current_temp, c.desired_temp, c.outside_temp);
        return stateRecords.reduce(rf, iv);
    }
    const temp_min = minOrMax(Math.min, 50);
    const temp_max = minOrMax(Math.max, -50);
    const chartYBase = 8;

    for (let i = xoff; i < expanded.length; i++) {
        const rec = expanded[i];
        const x = i - xoff;
        const scy = y => map(y, temp_min, temp_max, chartYBase, height);
        const cty = scy(rec.current_temp);
        const dty = scy(rec.desired_temp);
        const oat = scy(rec.outside_temp);

        strokeWeight(3);
        stroke('lightblue');
        line(x, chartYBase, x, cty);
        stroke('green');
        point(x, dty);
        stroke('black');
        point(x, oat);
        strokeWeight(3);
        if (rec.heater_is_on) {
            stroke('#9C2A00');
            point(x, 2);
        }
    }
    noLoop();
}

function addStateRecord(state) {
    stateRecords.push(state);
    loop();
}

function addAllStateRecords(records) {
    stateRecords = records;
    loop();
}

function expand(states) {
    if (states.length === 0) return states;

    const exp = [];

    let time = states[0].time;

    states.forEach((state, i) => {
      exp.push(state);
      while (i < states.length - 1 && time < states[i+1].time) {
        time += 15;
        const interpolatedState = Object.assign({}, state);
        interpolatedState.time = time;
        exp.push(interpolatedState);
      }
    });

    return exp;
}
