let stateRecords = [];

function setup() {
    const vis = $("#visualization");
    createCanvas(vis.width(), vis.height()).parent("visualization");
}

function draw() {
    frameRate(1);
    background('lightgray');
    translate(0, height);
    scale(1, -1);
    const expanded = expand(stateRecords);
    const xoff = max(0, expanded.length - width);
    for (let i = xoff; i < expanded.length; i++) {
        const rec = expanded[i];
        const x = i - xoff;
        const cty = rec.current_temp - 15;
        const dty = rec.desired_temp - 15;

        const vscale = 18;
        strokeWeight(3);
        stroke('blue');
        point(x, cty * vscale);
        stroke('green');
        point(x, dty * vscale);
        strokeWeight(5);
        if (rec.heater_is_on) {
            stroke('red');
            point(x, 5);
        }
    }
    // noLoop();
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
        exp.push({time: time, current_temp: state.current_temp, desired_temp: state.desired_temp, heater_is_on: state.heater_is_on});
      }
    });

    return exp;
}
