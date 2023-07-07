from ..instrument import Instrument
from ..instrumentJSParams import *


class NG7SANS(Instrument):
    """ A class to manipulate NG7SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
    """
    class_name = "NG7SANS"
    name_shown = "NG7 SANS"

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = name if name else "ng7"
        params = self.param_restructure(params)
        # Super is the Instrument class
        super().__init__(name, params)

    def load_params(self, params):
        """A method that loads the constants of the NG7SANS Instrument

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("NG7SANS Load Params")
        params["beam_stops"] = [2.54, 5.08, 7.62, 10.16]
        params["beam_stops"] = [{"beam_stop_diameter": beam_stop} for beam_stop in params.get("beam_stops", 2.54)]
        params["collimation"]["guides"]["gap_at_start"] = 188
        params["collimation"]["guides"]["guide_width"] = 5
        params["collimation"]["guides"]["transmission_per_guide"] = 0.974
        params["data"]["bs_factor"] = 1.05
        params["detectors"][0]["per_pixel_max_flux"] = 100
        params["data"]["peak_flux"] = 25500000000000
        params["data"]["peak_wavelength"] = 5.5
        params["data"]["beta"] = 0.0395
        params["data"]["charlie"] = 0.0442
        params["data"]["trans_1"] = 0.63
        params["data"]["trans_2"] = 0.7
        params["data"]["trans_3"] = 0.75
        params["detectors"][0]["pixel_size_x"] = 0.508
        params["detectors"][0]["pixel_size_y"] = 0.508
        params["detectors"][0]["pixel_size_x_unit"] = "cm"
        params["detectors"][0]["pixel_size_y_unit"] = "cm"
        params["detectors"][0]["pixel_no_x"] = 128
        params["detectors"][0]["pixel_no_y"] = 128
        params["detectors"][0]["pixel_no_z"] = 128
        params["collimation"]["aperture_offset"] = 5
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128
        params["collimation"]["guides"]["maximum_length"] = 1632
        params["collimation"]["guides"]["length_per_guide"] = 155
        if params.get("collimation").get("sample_space", "Huber") == "Huber":
            params["collimation"]["space_offset"] = 54.8  # HuberOffset
        else:
            params["collimation"]["space_offset"] = 0.0  # ChamberOffset

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "ng7sans.ncnr.nist.gov"

        super().load_objects(params)

    @staticmethod
    def get_js_params():
        """Creates a dictionary of js element_parameters to create html elements for the NG7SANS

        params[category][elementName] = {element_parameters}

        + **User editable elements:** sampleTable, wavelengthInput, wavelengthSpread, guideConfig, sourceAperture,
          sampleAperture,customAperture, sDDInputBox, sDDDefaults, offsetInputBox and offsetDefaults

        + **Read only elements:** beamFlux, figureOfMerit, attenuators, attenuationFactor,
          sSD, sDD, beamDiameter, beamStopSize, minimumQ, maximumQ, maximumVerticalQ, maximumHorizontalQ,
          source_apertures, and wavelength_ranges

        + **element_parameters**: name, default, type_val, unit, readonly, options, step, range_id,hidden, lower_limit,
          and upper_limit


        :return: Completed dictionary params[category][paramName] = js_element_array
        :rtype: Dict
        """
        params = generate_js_array()
        params["Sample"]["sampleTable"] = create_sample_table()
        params["Wavelength"]["wavelengthInput"] = create_wavelength_input()
        params["Wavelength"]["wavelengthSpread"] = create_wavelength_spread()
        params["Wavelength"]["beamFlux"] = create_beam_flux()
        params["Wavelength"]["figureOfMerit"] = create_figure_of_merit()
        params["Wavelength"]["attenuators"] = create_attenuators()
        params["Wavelength"]["attenuationFactor"] = create_attenuation_factor()
        params["Collimation"]["guideConfig"] = create_guide_config()
        params["Collimation"]["sourceAperture"] = create_source_aperture()
        params["Collimation"]["sampleAperture"] = create_sample_aperture()
        params["Collimation"]["customAperture"] = create_custom_aperture()
        params["Collimation"]["sSD"] = create_ssd()
        params["Detector"]["sDDInputBox"] = create_sdd_input_box()
        params["Detector"]["sDDDefaults"] = create_sdd_defaults()
        params["Detector"]["offsetInputBox"] = create_offset_input_box()
        params["Detector"]["offsetDefaults"] = create_offset_defaults()
        params["Detector"]["sDD"] = create_sdd()
        params["Detector"]["beamDiameter"] = create_beam_diameter()
        params["Detector"]["beamStopSize"] = create_beam_stop_size()
        params["QRange"]["minimumQ"] = create_min_q()
        params["QRange"]["maximumQ"] = create_max_q()
        params["QRange"]["maximumVerticalQ"] = create_max_vertical_q()
        params["QRange"]["maximumHorizontalQ"] = create_maximum_horizontal_q()
        params["hidden"]["source_apertures"] = {'0': [1.43, 2.54, 3.81], '1': [5.08], '2': [5.08], '3': [5.08],
                                                '4': [5.08], '5': [5.08], '6': [5.08], '7': [5.08], '8': [5.08],
                                                'LENS': [1.43],
                                                }
        params["hidden"]["wavelength_ranges"] = {"9.7": ['6.5', '20.0'], "13.9": ['4.8', '20.0'],
                                                 "15": ['4.5', '20.0'], "22.1": ['4.0', '20.0']}
        params["hidden"]["secondary_elements"] = encode_secondary_elements()
        params = check_params(params=params)
        return params
