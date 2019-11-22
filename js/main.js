function loadpage() {
    var ngb30ctx = document.getElementById('ngb30SansChart').getContext('2d');
    var ngb10ctx = document.getElementById('ngb10SansChart').getContext('2d');
    var ng7ctx = document.getElementById('ng7SansChart').getContext('2d');
    var vctx = document.getElementById('vsansChart').getContext('2d');
    // TODO: Create real base data sets
    var sansDataSets = [
        {
            label: 'Sample 1',
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
}

function updateConfiguration() {
    
}

function changeInstrument(instrument, instrumentOptions) {
    var inst = document.getElementById(instrument);
    var instruments = {};
    var instName = "";
    for (var i in instrumentOptions) {
        instName = instrumentOptions[i]
        instruments[instName] = document.getElementById(instName);
    }
    var selectStr = inst.options[inst.selectedIndex].value;
    for (var key in instruments) {
        if (key === selectStr) {
            instruments[key].style.display = "block";
        } else {
            instruments[key].style.display = "none";
        }
    }
}

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

window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};
