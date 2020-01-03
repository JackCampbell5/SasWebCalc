// Predefined chart colors
window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)',
    black: 'rgb(0, 0, 0)',
    white: 'rgb(255, 255, 255)'
};

// Default units for inputs
window.units = {
    "wavelength": "Å",
    "sampleAperture": "mm",
    "detectorOffset": "cm",
    "detectorDistance": "cm",
    "beamCenter": "cm",
}

// NGB 30m SANS
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
window.ngb30Constants = {
    'HuberOffset': '54.8',
    'HuberApertureOffset': '5.0',
    'ChamberOffset': '0.0',
    'ChamberApertureOffset': '5.0',
    'BSFactor': '1.05',
    'iPixel': '100.0',
    'aPixel': '5.08',
    'coeff': '10000',
    'xPixels': '128',
    'yPixels': '128',
    'serverName': 'ngb30sans.ncnr.nist.gov'
};

// NG7 SANS
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
window.ng7Constants = {
    'HuberOffset': '54.8',
    'ChamberOffset': '0.0',
    'ApertureOffset': '5.0',
    'BSFactor': '1.05',
    'iPixel': '100.0',
    'aPixel': '5.08',
    'coeff': '10000',
    'xPixels': '128',
    'yPixels': '128',
    'peakFlux': '2.55e13',
    'peakLambda': '5.5',
    'b': '0.0395',
    'c': '0.0442',
    'trans1': '0.63',
    'trans2': '0.7',
    'trans3': '0.75',
    'guideGap': '188',
    'guideWidth': '5',
    'guideLoss': '0.974',
    'serverName': 'ng7sans.ncnr.nist.gov'
};
window.ng7WavelengthRange = {
    "9.7": ['6.5', '20.0'],
    "11.5": ['5.5', '20.0'],
    "13.9": ['4.8', '20.0'],
    "22.1": ['4.0', '20.0']
};

// NGB 10m SANS
window.ngb10SourceApertures = {
    '0': ['1.3', '2.5', '3.8'],
    '1': ['5.0'],
    '2': ['5.0'],
};
window.ngb10Constants = {
    'HuberOffset': '0.0',
    'ChamberOffset': '0.0',
    'ApertureOffset': '5.0',
    'BSFactor': '1.05',
    'iPixel': '100.0',
    'aPixel': '5.08',
    'coeff': '10000',
    'xPixels': '128',
    'yPixels': '128',
    'serverName': 'ngbsans.ncnr.nist.gov'
};

// Models
window.modelList = {
    "debye": {
        "params": {
            "scale": 1000,
            "rg": 100,
            "bkg": 0.0
        }
    },
    "sphere": {
        "params": {
            "scale": 1,
            "radius": 1000,
            "sld_sphere": 1.0,
            "sld_solvent": 6.3,
            "bkg": 0.1,
        }
    }
}