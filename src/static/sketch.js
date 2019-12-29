function setup() {
    const vis = $("#visualization");
    createCanvas(vis.width(), vis.height()).parent("visualization");
    new EventSource('/status?interval=y').onmessage = event => addVizState(JSON.parse(event.data));
}

function draw() {
    background('lightgray');
    translate(0, height);
    scale(1, -1);
    const xoff = max(0, stateRecords.length - width);
    for (let i = xoff; i < stateRecords.length; i++) {
        const rec = stateRecords[i];
        const x = i - xoff;
        const cty = rec.current_temp - 15;
        const dty = rec.desired_temp - 15;

        const vscale = 9;
        stroke('blue');
        line(x, 0, x, cty * vscale);
        stroke('green');
        point(x, dty * vscale);
    }
    noLoop();
}

const stateRecords = [];

function addVizState(state) {
    stateRecords.push(state);
    loop();
}
