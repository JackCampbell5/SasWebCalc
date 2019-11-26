function loadpage() {
    var ngb30ctx = document.getElementById('ngb30SansChart').getContext('2d');
    var ngb10ctx = document.getElementById('ngb10SansChart').getContext('2d');
    var ng7ctx = document.getElementById('ng7SansChart').getContext('2d');
    var vctx = document.getElementById('vsansChart').getContext('2d');
    // TODO: Create real base data sets
    var sansDataSets = [
        {
            label: 'Data',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        }
    ]
    var vsansDataSets = [
        {
            label: 'Sample 1 - FT',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FL',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FR',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MT',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - ML',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - B',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        }
    ]

    var options = {
        responsive: true,
        title: {display: false },
        tooltips: {mode: 'index', intersect: false,},
        hover: {mode: 'nearest', intersect: true},
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: { display: true, labelString: "Q (Å^-1)"}
            }],
            yAxes: [{
                display: true,
                scaleLabel: { display: true, labelString: 'Relative Intensity (Au)'},
                ticks: {suggestedMin: 0, suggestedMax: 100, suggestedStepSize: 5}
            }]
        }
    }

    update1DChart(ngb30ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(ngb10ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(ng7ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(vctx, [0, 1, 2, 3, 4, 5], vsansDataSets, options);
    //restorePersistantState();
};

function updateConfiguration() {
    // TODO: Run calculation, update charts, etc.

}

function updateGuides(instrument, guideSelectStr) {
    var apertureNode = document.getElementById(instrument + "SourceAperture");
    var allApertureOptions = Object.values(apertureNode.options);
    var aperturesName = instrument + "SourceApertures";
    var guideApertureOptions = Object.values(window[aperturesName][guideSelectStr]).join(" ");
    for (aperture in allApertureOptions) {
        var apertureValue = allApertureOptions[aperture].value.toString();
        if (guideApertureOptions.includes(apertureValue)) {
            allApertureOptions[aperture].disabled = false;
            allApertureOptions[aperture].hidden = false;
            allApertureOptions[aperture].selected = true;
        } else {
            allApertureOptions[aperture].disabled = true;
            allApertureOptions[aperture].hidden = true;
        }
    }
    sessionStorage.setItem(instrument + "GuideConfig", guideSelectStr);
    updateConfiguration();
};

function updateAperture(instrument) {
    var instStr = instrument.toString();
    var customAperture = document.getElementById(instStr + 'CustomAperture');
    var customApertureLabel = document.getElementById(instStr + 'CustomApertureLabel');
    var sampleApertureSelector = document.getElementById(instStr + 'SampleAperture');
    if (sampleApertureSelector.value === "Custom") {
        customAperture.style.display = 'inline-block';
        customApertureLabel.style.display = 'inline-block';;
    } else {
        customAperture.style.display = 'none';
        customApertureLabel.style.display = 'none';
    }
}

function changeInstrument(domName, selectStr) {
    var inst = document.getElementById(domName);
    var instrumentOptions = [];
    for (var i = 0; i < inst.options.length; i++) {
        instrumentOptions.push(inst.options[i].value);
    }
    var instruments = {};
    var instName = "";
    for (var j in instrumentOptions) {
        instName = instrumentOptions[j]
        if (!(instName === "")) {
            instruments[instName] = document.getElementById(instName);
        }
    }
    for (var key in instruments) {
        if (key === selectStr) {
            instruments[key].style.display = "block";
        } else {
            instruments[key].style.display = "none";
        }
    }
    sessionStorage.setItem('instrument', selectStr);
    updateConfiguration();
};

function update1DChart(chartElement, xAxis, yDataSets, dataOptions) {
    var chart = new Chart(chartElement, {
        type: 'line',
        data: {
            labels: xAxis,
            datasets: yDataSets
        },
        options: dataOptions
    });
}

function restorePersistantState() {
    // TODO: Update values on screen when values are loaded
    var instrument = sessionStorage.getItem('instrument');
    var instSelector = document.getElementById('instrumentSelector');
    instSelector.value = instrument;
    var ng7GuideConfig = sessionStorage.getItem('ng7GuideConfig');
    var ng7GuideSelector = document.getElementById('ng7GuideConfig');
    ng7GuideSelector.value = ng7GuideConfig;
    updateConfiguration();
}

window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

window.ngb30SourceApertures = {
    '0': ['1.43', '2.54', '3.81'],
    '1': ['5.08'],
    '2': ['5.08'],
    '3': ['5.08'],
    '4': ['5.08'],
    '5': ['5.08'],
    '6': ['5.08'],
    '7': ['5.00', '2.50', '0.95'],
    '8': ['5.08'],
    'LENS': ['1.43'],
};

window.ng7SourceApertures = {
    '0': ['1.43', '2.54', '3.81'],
    '1': ['5.08'],
    '2': ['5.08'],
    '3': ['5.08'],
    '4': ['5.08'],
    '5': ['5.08'],
    '6': ['5.08'],
    '7': ['5.08'],
    '8': ['5.08'],
    'LENS': ['1.43'],
};

window.ngb10SourceApertures = {
    '0': ['1.3', '2.5', '3.8'],
    '1': ['5.0'],
    '2': ['5.0'],
};
