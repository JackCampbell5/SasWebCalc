from ..instrument import Instrument


class NGB10SANS(Instrument):
    """ A class to manipulate NGB10SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
    """
    class_name = "NGB10SANS"
    name_shown = "NGB 10m SANS"

    # Class for the NGB 10m SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = name if name else "ngb10"
        params = self.param_restructure(params)
        super().__init__(name, params)

    def load_params(self, params):
        """A method that loads the constants of the NG7SANS Instrument

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("NGB10SANS Load Params")
        params["data"] = {}
        params["data"]["bs_factor"] = 1.05
        params["detectors"][0]["per_pixel_max_flux"] = 100.0
        params["data"]["peak_flux"] = 2.5e13
        params["data"]["peak_wavelength"] = 5.5
        params["data"]["beta"] = 0.03
        params["data"]["charlie"] = 0.03
        params["data"]["trans_1"] = 0.63
        params["data"]["trans_2"] = 1.0
        params["data"]["trans_3"] = 0.75
        params["detectors"][0]["pixel_size_x"] = 0.508
        params["detectors"][0]["pixel_size_y"] = 0.508
        params["detectors"][0]["pixel_size_x_unit"] = "cm"
        params["detectors"][0]["pixel_size_y_unit"] = "cm"
        params["detectors"][0]["pixel_no_x"] = 128
        params["detectors"][0]["pixel_no_y"] = 128
        params["detectors"][0]["pixel_no_z"] = 128
        params["collimation"]["guides"]["gap_at_start"] = 165
        params["collimation"]["guides"]["guide_width"] = 5
        params["collimation"]["guides"]["transmission_per_guide"] = 0.974
        params["collimation"]["guides"]["maximum_length"] = 513
        if params["collimation"]["guides"]["number_of_guides"] != 0:
            params["collimation"]["guides"]["length_per_guide"] = 150 + (
                    61.9 / params["collimation"]["guides"]["number_of_guides"])
        params["collimation"]["aperture_offset"] = 5
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128
        if params.get("collimation").get("sample_space", "Huber") == "Huber":
            params["collimation"]["space_offset"] = 0  # HuberOffset
        else:
            params["collimation"]["space_offset"] = 0  # ChamberOffset

        # Temporary constants not in use anymore
        params["temp"] = {}
        params["temp"]["serverName"] = "ngbsans.ncnr.nist.gov"
        super().load_objects(params)

    def calculate_source_to_sample_aperture_distance(self):
        """Calculates the source to sample aperture distance from the guide values and space offset

        :return: The value of the SSAD
        :rtype: None
        """
        # TODO: This runs way to many times
        ssd_temp = self.collimation.guides.get_maximum_length() - self.collimation.space_offset
        if self.collimation.guides.number_of_guides != 0:
            ssd_temp = ssd_temp - (self.d_converter(61.9, 'cm')) - (
                    self.collimation.guides.get_length_per_guide() * self.collimation.guides.number_of_guides)
        self.collimation.ssad = ssd_temp - self.collimation.get_sample_aperture_offset()
        return self.collimation.ssad
