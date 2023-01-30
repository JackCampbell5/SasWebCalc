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
    "sampleAperture": "cm",
    "source_aperture": "cm",
    "detectorOffset": "cm",
    "detectorDistance": "cm",
    "beamCenter": "cm",
    "beamDiameter": "cm",
    "beamStopDiameter":"inch"
}

// Inputs for averaging types
window.averagingInputs = {
    "circular": [],
    "sector": ["phi", "dPhi", "detectorSections"],
    "annular": ["qCenter", "qWidth"],
    "rectangular": ["qWidth", "phi", "detectorSections"],
    "elliptical": ["phi", "aspectRatio", "detectorSections"]
}

// Default configuration values onloading the page
window.defaultConfiguration = {
    "areaDetector.beamCenterX": "64.5cm",
    "areaDetector.beamCenterY": "64.5cm",
    "attenuator.key": 0,
    "beamStop.beamStop": 2,
    "beamStopX.softPosition": "0.0cm",
    "BeamStopY.softPosition": "0.0cm",
    "detectorOffset.softPosition": "0.0cm",
    "geometry.externalSampleApertureShape": "CIRCLE",
    "geometry.externalSampleAperture": "12.7mm",
    "geometry.sampleToAreaDetector": "100cm",
    "guide.guide": 0,
    "guide.sourceAperture": "5.08",
    "wavelength.wavelength": "6",
    "wavelengthSpread.wavelengthSpread": 0.115,
};

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
    'ChamberOffset': '0.0',
    'ApertureOffset': '5.0',
    'BSFactor': '1.05',
    'iPixel': '100.0',
    'aPixel': '5.08',
    'coeff': '10000',
    'xPixels': '128',
    'yPixels': '128',
    'peakFlux': '2.42e13',
    'peakLambda': '5.5',
    'b': '0.0',
    'c': '-0.0243',
    'trans1': '0.63',
    'trans2': '1.0',
    'trans3': '0.75',
    'guideGap': '100',
    'guideWidth': '6.0',
    'guideLoss': '0.924',
    'serverName': 'ngb30sans.ncnr.nist.gov'
};
window.ngb30WavelengthRange = {
    "10.9": ['6.0', '20.0'],
    "12.1": ['5.5', '20.0'],
    "13.8": ['4.5', '20.0'],
    "16.8": ['3.0', '20.0'],
    "25.6": ['3.0', '20.0']
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
    'serverName': 'ng7sans.ncnr.nist.gov',
    //Not a use var
    'HuberOffset': '54.8',
    //Aperture offset does not seem to be used
    'ChamberOffset': '0.0',
    //Pramaters for calculateQRangeSlicer which does nto exist in python yet
    'ApertureOffset': '5.0',
    'coeff': '10000',
    'xPixels': '128',
    'yPixels': '128',
    //Detector class???
    'aPixel': '5.08', //pixel_size_x
    'iPixel': '100.0',
    //Data class
    //Data class
    'BSFactor': '1.05', //bs_factor
    'peakFlux': '2.55e13',//peak_flux
    'peakLambda': '5.5', //peak_wavelength
    'b': '0.0395',//beta
    'c': '0.0442', //charlie
    'trans1': '0.63', //trans_1
    'trans2': '0.7', //trans_2
    'trans3': '0.75',//trans_3
    //Guide class constants needed
    'guideGap': '188', //gap_at_start
    'guideWidth': '5', //guide_width
    'guideLoss': '0.974' //GuideLoss
};
window.ng7WavelengthRange = {
    "9.7": ['6.5', '20.0'],
    "13.9": ['4.8', '20.0'],
    "15": ['4.5', '20.0'],
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
    'peakFlux': '2.5e13',
    'peakLambda': '5.5',
    'b': '0.03',
    'c': '0.03',
    'trans1': '0.63',
    'trans2': '1.0',
    'trans3': '0.75',
    'guideGap': '165',
    'guideWidth': '5',
    'guideLoss': '0.974',
    'serverName': 'ngbsans.ncnr.nist.gov'
};
window.ngb10WavelengthRange = {
    "9.2": ['5.5', '20.0'],
    "12": ['4.0', '20.0'],
    "14": ['3.0', '20.0'],
    "25": ['3.0', '20.0']
};

// Models
window.modelList = {
};