function setup() {
    const vis = $("#visualization");
    createCanvas(vis.width(), vis.height()).parent("visualization");
    new EventSource('/status?interval=y').onmessage = event => addVizState(JSON.parse(event.data));
}

function draw() {
    background('lightgray');
    translate(0, height);
    scale(1, -9);
    stroke('blue');
    const xoff = max(0, stateRecords.length - width);
    for (let i = xoff; i < stateRecords.length; i++) {
        const rec = stateRecords[i];
        const x = i - xoff;
        const cty = rec.current_temp - 15;
        const dty = rec.desired_temp - 15;

        function drawDesired() {
            stroke('green');
            line(x, 0, x, dty);
        }

        function drawCurrent() {
            stroke('blue');
            line(x, 0, x, cty);
        }

        if (cty > dty) {
            drawCurrent();
            drawDesired();
        } else {
            drawDesired();
            drawCurrent();
        }
    }
    noLoop();
}

const stateRecords = [];

function addVizState(state) {
    stateRecords.push(state);
    loop();
}
