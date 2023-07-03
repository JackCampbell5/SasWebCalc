from ..instrument import Instrument
from ..instrumentJSParams import create_js, generate_js_array


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
        params = generate_js_array()
        # params["ng7BeamStopSizes"] = create_js(options=[2.54, 5.08, 7.62, 10.16])
        params["Sample"]["SampleTable"] = create_js(name='Sample Table', default="Chamber", type="select",
                                                    options=['Chamber', 'Huber'], unit='')
        params["Wavelength"]["WavelengthInput"] = create_js(name='Wavelength', default=6.0, min=4.8, max=20.0,
                                                            type="number", unit='nm;')
        params["Wavelength"]["WavelengthSpread"] = create_js(name='Wavelength Spread', default=13.9, type="select",
                                                             unit='', options=[9.7, 13.9, 15, 22.1])
        params["Wavelength"]["BeamFlux"] = create_js(name='Beam Flux', default='', type="number",
                                                     unit='n cm<sup>-2</sup> s<sup>-1</sup>', readonly=True)
        params["Wavelength"]["FigureOfMerit"] = create_js(name='Figure of merit', default='', type="number", unit='',
                                                          readonly=True)
        params["Wavelength"]["Attenuators"] = create_js(name='Attenuators', default='', type="number", unit='',
                                                        readonly=True)
        params["Wavelength"]["AttenuationFactor"] = create_js(name='Attenuation Factor', default='', type="number",
                                                              unit='', readonly=True)
        params["Collimation"]["GuideConfig"] = create_js(name='Guides', default=0, type="select", unit='',
                                                         options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS'])
        params["Collimation"]["SourceAperture"] = create_js(name='Source Aperture', default=1.43, type="select",
                                                            unit='cm', options=[1.43, 2.54, 3.81, 5.08])
        params["Collimation"]["SampleAperture"] = create_js(name='Sample Aperture', default=0.500, type="select",
                                                            unit='inch',
                                                            options=[0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75,
                                                                     0.875, 1.00, 'Custom'])
        params["Collimation"]["CustomAperture"] = create_js(name='Aperture Diameter', default=13, type="number",
                                                            unit='mm', hidden=True)
        params["Collimation"]["SSD"] = create_js(name='Source-To-Sample Distance', default=1627, type="number",
                                                 unit='cm', readonly=True)
        params["Detector"]["SDDInputBox"] = create_js(name='Detector Distance', default=100, type="number", unit='cm')
        params["Detector"]["SDDDefaults"] = create_js(name='', default=100, type="range", range_id='SDDDefaultRange',
                                                      unit='', lower_limit=90, upper_limit=1532,
                                                      options=[100, 400, 1300, 1530])
        params["Detector"]["OffsetInputBox"] = create_js(name='Detector Offset', default=0, type="number", unit='cm')
        params["Detector"]["OffsetDefaults"] = create_js(name='', default=0, type="range",
                                                         range_id='OffsetDefaultRange', unit='', lower_limit=0,
                                                         upper_limit=25, options=[0, 5, 10, 15, 20, 25])
        params["Detector"]["SDD"] = create_js(name='Sample-To-Detector Distance', default=100, type="number", unit='cm',
                                              readonly=True)
        params["Detector"]["BeamDiameter"] = create_js(name='Beam Diameter', default='', type="number", unit="cm",
                                                       readonly=True)
        params["Detector"]["BeamStopSize"] = create_js(name='Beam Stop Diameter', default='', type="number", unit="cm",
                                                       readonly=True)
        params["QRange"]["MinimumQ"] = create_js(name='Minimum Q', default='', type="number", unit="Å;<sup>-1</sup>",
                                                 readonly=True)
        params["QRange"]["MaximumQ"] = create_js(name='Maximum Q', default='', type="number", unit="Å;<sup>-1</sup>",
                                                 readonly=True)
        params["QRange"]["MaximumVerticalQ"] = create_js(name='Maximum Vertical Q', default='', type="number",
                                                         unit="Å;<sup>-1</sup>", readonly=True)
        params["QRange"]["MaximumHorizontalQ"] = create_js(name='Maximum Horizontal Q', default='', type="number",
                                                           unit="Å;<sup>-1</sup>", readonly=True)
        output = {"params": params, "other_params": {}}
        output["other_params"]["source_apertures"] = {'0': [1.43, 2.54, 3.81], '1': [5.08], '2': [5.08], '3': [5.08],
                                                      '4': [5.08], '5': [5.08], '6': [5.08], '7': [5.08], '8': [5.08],
                                                      'LENS': [1.43],
                                                      }
        output["other_params"]["wavelength_ranges"] = {"9.7": ['6.5', '20.0'], "13.9": ['4.8', '20.0'],
                                                       "15": ['4.5', '20.0'], "22.1": ['4.0', '20.0']}
        return output
