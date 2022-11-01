class Constants:
    def __init__(self):
        self.constants = {'units': {
            "wavelength": "Å",
            "sampleAperture": "mm",
            "detectorOffset": "cm",
            "detectorDistance": "cm",
            "beamCenter": "cm",
            "beamDiameter": "cm",
            "beamStopDiameter": "inch"
        },

            'averagingInputs': {
                "circular": [],
                "sector": ["phi", "dPhi", "detectorSections"],
                "annular": ["qCenter", "qWidth"],
                "rectangular": ["qWidth", "phi", "detectorSections"],
                "elliptical": ["phi", "aspectRatio", "detectorSections"]
            },
            'defaultConfiguration': {
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
            }
        }  # End constant dictionary creation

    def get_constant(self, typeParam, name):
        return self.constants[typeParam][name]
