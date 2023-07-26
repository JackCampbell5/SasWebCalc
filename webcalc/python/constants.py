class Constants:
    """A class for storing constants

    :param dict self.constants: A dictionary of constants
    """

    def __init__(self):
        """Creates object parameters for BeamStop class and runs set params method
        Sets object self.constants

        :rtype: None
        :return: Nothing as it just creates an object
        """
        self.constants = {
            'units': {"wavelength": "Å", "sampleAperture": "mm", "detectorOffset": "cm", "detectorDistance": "cm",
                      "beamCenter": "cm", "beamDiameter": "cm", "beamStopDiameter": "inch"
                      },

            'averagingInputs': {"circular": [], "sector": ["phi", "dPhi", "detectorSections"],
                                "annular": ["qCenter", "qWidth"], "rectangular": ["qWidth", "phi", "detectorSections"],
                                "elliptical": ["phi", "aspectRatio", "detectorSections"]
                                },
            'defaultConfiguration': {"areaDetector.beamCenterX": "64.5cm", "areaDetector.beamCenterY": "64.5cm",
                                     "attenuator.key": 0, "beamStop.beamStop": 2, "beamStopX.softPosition": "0.0cm",
                                     "BeamStopY.softPosition": "0.0cm", "detectorOffset.softPosition": "0.0cm",
                                     "geometry.externalSampleApertureShape": "CIRCLE",
                                     "geometry.externalSampleAperture": "12.7mm",
                                     "geometry.sampleToAreaDetector": "100cm", "guide.guide": 0,
                                     "guide.sourceAperture": "5.08", "wavelength.wavelength": "6",
                                     "wavelengthSpread.wavelengthSpread": 0.115,
                                     }
        }  # End constant dictionary creation

    def get_constant(self, type_param, name):
        """

        :param str type_param: The type of the parameter
        :param str name: The name of the specific parameter
        :return: The constant that is requested
        :rtype: Str and float
        """
        return self.constants[type_param][name]


class VSANS_Constants:
    def __init__(self):
        self.constants = None

    def get_constants(self, preset, VSANS_dict, js_only=False):
        # Gets the constants based on the preset
        if preset == "16m":
            self.constants = self._preset_16m(VSANS_dict)
        elif preset == "11m":
            self.constants = self._preset_11m(VSANS_dict)
        elif preset == "4.5m":
            self.constants = self._preset_4_5m(VSANS_dict)
        else:
            self.constants = self._preset_19m(VSANS_dict)
        # If you only want the Js params just return the user ones
        if js_only:
            return self.constants.get("user", {})
        else:
            return self.constants.get("other",{})

    def _preset_4_5m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "9"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 579
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 450  # SDD_middle_input
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 100
        user_inaccessible["front_left_panel"]["lateralOffset"] = -10.344
        user_inaccessible["front_right_panel"]["lateralOffset"] = 7.57
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_11m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "7"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 980
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1100  # SDD_middle_input
        other_constants["beamstop_index"] = 4 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 230
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.32
        user_inaccessible["front_right_panel"]["lateralOffset"] = 6.82
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_16m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "2"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 2157
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1600  # SDD_middle_input
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 350
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.627
        user_inaccessible["front_right_panel"]["lateralOffset"] = 7.0497
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_19m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6  # lambda
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "0"
        user_inaccessible["collimation"]["sourceAperture_js"] = "30.0"  # source_aperture_str
        user_inaccessible["collimation"]["sourceDistance"] = 2441  # source_distance
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1900  # SDD_middle_input
        other_constants["beamstop_index"] = 2 - 1
        user_inaccessible["mid_left_panel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 400
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.24
        user_inaccessible["front_right_panel"]["lateralOffset"] = 6.766
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}
