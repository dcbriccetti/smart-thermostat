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

    if (stateRecords.length === 0) return;

    function minOrMax(fn, iv) {
        const rf = (a, c) => fn(a, c.current_temp, c.desired_temp, c.outside_temp);
        return stateRecords.reduce(rf, iv);
    }

    const temp_min = minOrMax(Math.min, 50);
    const temp_max = minOrMax(Math.max, -50);
    const chartYBase = 8;

    const sliceSecs = 15;
    const elapsed = stateRecords[stateRecords.length - 1].time - stateRecords[0].time;
    const numSlices = min(width - 10, int(elapsed / sliceSecs));

    const secsSinceLastSample = int(Date.now() / 1000 - stateRecords[stateRecords.length - 1].time);
    const multOfSliceSecsSinceLastSample = int(secsSinceLastSample / sliceSecs);
    let timeEnd = stateRecords[stateRecords.length - 1].time + multOfSliceSecsSinceLastSample * sliceSecs;

    let x = width - 1;
    let iState = stateRecords.length - 1;

    function tempAge(rec) {
        return (rec.time - rec.outside_temp_collection_time) / 60;
    }

    for (let i = 0; i < numSlices; ++i) {
        let timeStart = timeEnd - sliceSecs;
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

            strokeWeight(3);
            stroke('lightblue');
            line(x, chartYBase, x, cty);

            stroke('green');
            point(x, dty);

            const opacity = map(min(avgOATempAges, 60), 0, 60, 255, 0);
            stroke(0, 0, 0, opacity);
            point(x, oat);

            if (heatOnInPeriod) {
                stroke('#9C2A00');
                point(x, 2);
            }
        }

        --x;
        timeEnd -= sliceSecs;
    }
}

function addStateRecord(state) {
    stateRecords.push(state);
}

function addAllStateRecords(records) {
    stateRecords = records;
}
