import math
from typing import Union

from ..instrument import BeamStop, Collimation, Detector, Data, NUMBER_TYPE, Wavelength
from ..instrumentJSParams import generate_js_array
from ..slicers import Circular, Elliptical, Rectangular, Sector
from ..units import Converter


class Instrument:
    """ The master class for storing and manipulating Instrument related data.

    :param String self.averaging_type: The averaging type for slicer
    :param  self.slicer_params: Parameters for slicer
    :param Slicer self.slicer: A slicer object for the calculation of the predicted data
    :param Converter self.d_converter: A distance converter object, typically in CM
    :param Converter self.t_converter: A time converter object, typically in s
    :param Data self.data: A Data object that contains more parameters
    :param Collimation self.collimation: A collection object that handles collection related data
    :param Wavelength self.wavelength: A wavelength object that handles wavelength related data
    :param Detector self.detectors: A detector object that handles detector related data
    :param BeamStop self.beam_stops: A beam stop object that handles beam stop related data
    :param Float self.beam_flux: The beam flux of the calculation
    :param Dict self.one_dimensional: One denominational data
    :param Dict self.two_dimensional: Two denominational data
    :param String self.name: The name of the selected instrument
    :param Dict self.params: A dictionary of parameters received from the JavaScript
    """
    isReal = False

    def __init__(self, name="", params=None):
        """Creates object parameters for Instrument class and runs set the params parameter which runs the load params methods

        :param str name: The instrument name
        :param dict params: The dictionary of params
        :return: None as it just sets the parameters
        :rtype: None
        """
        # Unit converters
        self.averaging_type = None
        self.slicer_params = None
        self.slicer = []
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.data = None
        self.collimation = None
        self.wavelength = None
        self.detectors = []
        self.beam_stops = None
        self.beam_flux = None
        self.one_dimensional = {"I": None, "dI": None, "Q": None, "dQ": None, "fSubS": None}
        self.two_dimensional = {"I": None, "dI": None, "Qx": None, "dQx": None, "Qy": None, "dQy": None, "fSubS": None}
        if not params:
            params = {}  # Only store values used for calculations in Instrument class
        self.name = name
        self._params = params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        """Runs the load params method when params is originally set

        :param params:
        :return:
        """
        self.load_params(params)

    def load_params(self, params):
        """Runs the load object methods.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        # """Pseudo-abstract method to initialize constants associated with an instrument"""
        # raise NotImplementedError(f"Instrument {self.name} has not implemented the `load_params` method.")
        self.load_objects(params)

    def param_restructure(self, calculate_params):
        """ A method that takes the list of params from the Javascript and assigns it to a dictionary allowing the python to assign variables to objects

        :param dict calculate_params: A dictionary of the values gotten from the js
        :return: An array of the params
        :rtype: Dict
        """
        old_params = calculate_params["instrument_params"]

        def _param_get_helper(name="", category="", key="default", default_value=None, division=1):
            """ Checks if a value exists at a certain key and if not sets the value to none ot be removed later

            :param str name: the dictionary of parameters to get the value from
            :param str key: The name of the key you want the value of
            :param default_value: The default value if none exists at that location in the params dictionary
            :param int division: The number to device by if necessary for debuting
            :return: The value at the keys position in the dictionary or None
            :rtype: str, None
            """
            params = old_params.get(category, {}).get(name, {})
            try:
                result = params.get(key, default_value)
                if division != 1:
                    result = result / 100
            except AttributeError:
                return None
            # If it is blank make the value none
            if result == "":
                return default_value
            return result

        # Instrument class parameters
        self.beam_flux = _param_get_helper(name="beamFlux", category="Wavelength")

        params = {}
        # Collimation
        params["collimation"] = {}
        params["collimation"]["guides"] = {}
        params["collimation"]["guides"]["lenses"] = self.guide_lens_config(
            _param_get_helper(name="guideConfig", category="Collimation"), False)
        params["collimation"]["guides"]["number_of_guides"] = self.guide_lens_config(
            _param_get_helper(name="guideConfig", category="Collimation"), True)
        params["collimation"]["detector_distance"] = _param_get_helper(name="sDDInputBox", category="Detector")
        if "sampleTable" in old_params.values():
            params["collimation"]["sample_space"] = _param_get_helper(name="sampleTable", category="Sample")
        params["collimation"]["ssad_unit"] = _param_get_helper(name="sSD", category="Collimation", key="unit")
        params["collimation"]["ssad"] = _param_get_helper(name="sSD", category="Collimation")
        params["collimation"]["ssd_unit"] = _param_get_helper(name="sSD", category="Collimation", key="unit")
        params["collimation"]["ssd"] = _param_get_helper(name="sSD", category="Collimation")

        # Collimation - sample_aperture
        params["collimation"]["sample_aperture"] = {}
        # Better arrangement for the get statements below - missing  else None from Jeff's changes
        params["collimation"]["sample_aperture"]["diameter"] = _param_get_helper(name="sampleAperture",
                                                                                 category="Collimation")
        params["collimation"]["source_aperture"] = {}
        params["collimation"]["source_aperture"]["diameter_unit"] = _param_get_helper(name="sourceAperture",
                                                                                      category="Collimation",
                                                                                      key="unit")
        params["collimation"]["source_aperture"]["diameter"] = _param_get_helper(name="sourceAperture",
                                                                                 category="Collimation")

        # Data
        params["data"] = {}
        params["data"]["beam_diameter"] = _param_get_helper(name="beamDiameter", category="Detector")
        params["data"]["beam_diameter_unit"] = _param_get_helper(name="beamDiameter", category="Detector", key="unit")
        params["data"]["calculated_beam_stop_diameter"] = _param_get_helper(name="beamStopSize", category="Detector")
        params["data"]["figure_of_merit"] = _param_get_helper(name="figureOfMerit", category="Wavelength")
        params["data"]["flux"] = _param_get_helper(name="beamFlux", category="Wavelength")

        # Detectors
        params["detectors"] = [None]
        params["detectors"][0] = {}
        offset_params = old_params.get("Detector", {}).get("offsetInputBox",{})
        if any(offset_params):
            params["detectors"][0]["offset_unit"] = _param_get_helper(name="offsetInputBox", category="Detector",
                                                                      key="unit")
            params["detectors"][0]["offset"] = _param_get_helper(name="offsetInputBox", category="Detector")
        params["detectors"][0]["sdd_unit"] = _param_get_helper(name="sDDInputBox", category="Detector", key="unit")
        params["detectors"][0]["sdd"] = _param_get_helper(name="sDDInputBox", category="Detector")

        # Slicer
        params["slicer"] = {}
        params["average_type"] = calculate_params["slicer"]

        # Wavelength
        params["wavelength"] = {}
        params["wavelength"]["attenuation_factor"] = _param_get_helper(name="attenuationFactor", category="Wavelength")
        params["wavelength"]["number_of_attenuators"] = _param_get_helper(name="customAperture", category="Collimation")
        params["wavelength"]["wavelength_spread_unit"] = _param_get_helper(name="wavelengthSpread",
                                                                           category="Wavelength", key="unit")
        params["wavelength"]["wavelength_spread"] = _param_get_helper(name="wavelengthSpread", category="Wavelength",
                                                                      division=100)
        params["wavelength"]["wavelength_unit"] = _param_get_helper(name="wavelengthInput", category="Wavelength",
                                                                    key="unit")
        params["wavelength"]["wavelength"] = _param_get_helper(name="wavelengthInput", category="Wavelength")

        # Removes the None values so they can be set to the default value
        return self._remove_nones(params)

    def _remove_nones(self, params: dict) -> dict:
        """A recursive method to remove any dictionary values that are None

        :param params: A dictionary that may or may not have values that are None.
        :return: A new dictionary where None values are removed
        :rtype: dict
        """
        new_dict = {}
        for name, value in params.items():
            if value is not None:
                if isinstance(value, dict):
                    # Recurse into the method to remove Nones from the sub-dictionary
                    value = self._remove_nones(value)
                new_dict[name] = value
        return new_dict

    def guide_lens_config(self, value, guide_param):
        """Helper functions which helps set values in relation to guides

        If guide param the value being set is the # of guides
        If the guide_param is false the value being set is boolean value of LENSes

        :param str value: The value the user input on the JS side
        :param boolean guide_param: The boolean value that is true for # of guides and false for lenses
        :return: An int or a boolean based on what was requested
        :rtype: int and boolean
        """
        if value == "LENS":
            if guide_param:
                return 0
            else:
                return True
        else:
            if guide_param:
                return value
            else:
                return False

    def load_objects(self, params):
        """A function that creates the objects necessary for the calculations

        Create objects beam_stops, detectors, collimation, and wavelength

        :param dict params: A dictionary of parameters to send to the initialization of the objects
        :return: Nothing as it just sets up all the objects
        :rtype: None
        """
        # Creates the objects with the param array
        #       (This is not a part of load params so instrument can have default values if necessary)

        # CAF Beam stop defined
        self.beam_stops = [BeamStop(self, beamstop_params) for beamstop_params in
                           params.get('beam_stops', [{'beam_stop_diameter': 2.54}])]
        self.detectors = [Detector(self, detector_params) for detector_params in params.get('detectors', [{}])]
        self.collimation = Collimation(self, params.get('collimation', {}))
        self.wavelength = Wavelength(self, params.get('wavelength', {}))
        self.data = Data(self, params.get('data', {}))

        # gets the parameters for slicer object and updates the parameters dictionary for that

        # Creates slicer param objects
        self.averaging_type = params.get("average_type", "ERROR")
        self.slicer_params = params.get('slicer', {})

    def sas_calc(self) -> dict[str, Union[NUMBER_TYPE, str, list[Union[NUMBER_TYPE, str]]]]:
        """ The main function that runs all the calculation and returns the results

        Makes a user inaccessible sub dictionary witch contains the results to be sent back to the instrument JS

        :return: A dictionary of the calculation results
        :rtype: Dict
        """
        # MainFunction for this class

        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculate_instrument_parameters()

        # Final output returned to the JS
        python_return = {}
        python_return["user_inaccessible"] = generate_js_array(name=False)
        python_return["user_inaccessible"]["Wavelength"]["beamFlux"] = self.data.flux
        python_return["user_inaccessible"]["Wavelength"]["figureOfMerit"] = self.data.figure_of_merit
        python_return["user_inaccessible"]["Wavelength"]["attenuators"] = self.get_attenuator_number()
        python_return["user_inaccessible"]["Collimation"]["sSD"] = self.collimation.ssd
        python_return["user_inaccessible"]["Detector"]["sDD"] = self.detectors[0].get_sdd()
        python_return["user_inaccessible"]["Detector"]["beamDiameter"] = int(self.get_beam_diameter() * 10000) / 10000
        python_return["user_inaccessible"]["Detector"]["beamStopSize"] = self.data.calculated_beam_stop_diameter
        python_return["user_inaccessible"]["Wavelength"]["attenuationFactor"] = self.get_attenuation_factor()
        python_return["user_inaccessible"]["QRange"]["maximumVerticalQ"] = self.data.q_max_vert
        python_return["user_inaccessible"]["QRange"]["maximumHorizontalQ"] = self.data.q_max_horizon
        python_return["user_inaccessible"]["QRange"]["maximumQ"] = self.data.q_max
        python_return["user_inaccessible"]["QRange"]["minimumQ"] = self.data.q_min
        python_return["data"] = {}
        for i, slicer in enumerate(self.slicer):
            python_return["data"][i] = {}
            python_return["data"][i]["nCells"] = slicer.n_cells.tolist()
            python_return["data"][i]["qsq"] = slicer.d_sq.tolist()
            python_return["data"][i]["sigmaAve"] = slicer.sigma_ave.tolist()
            python_return["data"][i]["qAverage"] = slicer.q_average.tolist()
            python_return["data"][i]["sigmaQ"] = slicer.sigma_q.tolist()
            python_return["data"][i]["fSubs"] = slicer.f_subs.tolist()
            python_return["data"][i]["qxValues"] = slicer.qx_values.tolist()
            python_return["data"][i]["qyValues"] = slicer.qy_values.tolist()
            python_return["data"][i]["q2DValues"] = slicer.q_2d_values.tolist()
            python_return["data"][i]["intensity2D"] = slicer.intensity_2D.tolist()
            python_return["data"][i]["qValues"] = slicer.q_values.tolist()
            python_return["data"][i]["slicer_params"] = slicer.slicer_return()
        # Return bare dictionary to allow easier access to data upstream
        #  Note - this forces JSON encoding upstream
        return python_return

    def calculate_instrument_parameters(self):
        """Uses the many functions to calculate all the necessary parameters necessary for an instrument

        * This function is usually called by the sas calc function
        * Calculates beam stop diameter, beam flux, figure of merit, attenuator number, slicer array values, sdd, and min and max q values

        :return: It returns nothing as each function sets the value it calculates
        :rtype: None
        """
        self.calculate_sample_to_detector_distance()
        # Calculate the estimated beam flux
        self.data.calculate_beam_flux()
        # Calculate the figure of merit
        self.data.calculate_figure_of_merit()
        # Calculate the number of attenuators
        self.calculate_attenuator_number()
        self.data.calculate_min_and_max_q()
        self.calculate_slicer()

    def calculate_attenuation_factor(self, index=0):
        """Calculates the attenuation factors from the sample aperture diameter and returns the calculated value

        * Usually run by the calculate attenuator number function

        :param index: The index of the value to find in the detectors array
        :return: Returns the float value of the calculated attenuation factor
        :rtype: Float
        """
        a2 = self.get_sample_aperture_diam()  # Good
        beam_diam = self.get_beam_diameter(index)
        # Start 3/29 fix beam diameter
        a_pixel = self.detectors[index].get_pixel_size_x() / 100  # Good
        i_pixel_max = self.detectors[index].per_pixel_max_flux  # Good
        num_pixels = (math.pi / 4) * (0.5 * (a2 + beam_diam) / a_pixel) ** 2
        i_pixel = self.get_beam_flux() / num_pixels
        atten = 1.0 if i_pixel < i_pixel_max else i_pixel_max / i_pixel
        self.wavelength.attenuation_factor = atten if atten == 1.0 else round(atten * 100000) / 100000
        return self.wavelength.attenuation_factor

    def calculate_attenuator_number(self):
        """ Calculates the number of attenuators present based on the attenuation factor and wavelength

        * Usually run by calculate_instrument_parameters and runs calculate_attenuation_factor

        :return: The number of attenuators
        :rtype: int
        """
        self.calculate_attenuation_factor()
        atten = self.get_attenuation_factor()
        if atten:
            af = 0.498 + 0.0792 * self.get_wavelength() - 1.66e-3 * self.get_wavelength() ** 2
            nf = -1 * math.log(atten) / af
            num_atten = math.ceil(nf)
            if num_atten > 6:
                num_atten = 7 + math.floor((num_atten - 6) / 2)
        else:
            num_atten = 0
        self.wavelength.number_of_attenuators = num_atten
        return num_atten

    def calculate_beam_stop_projection(self, index=0):
        """ The beam stop casts a shadow based on the distance the beam stop is from the detector, creating a
        larger projection than the nominal size of the beam stop. This method calculates that shadow.

        :param int index: The index in the detector array
        :return: The calculated size of the projected beam stop
        :rtype: Float
        """
        self.get_sample_to_detector_distance(index)
        self.data.calculate_beam_stop_diameter(index)
        bs_diam = self.get_beam_stop_diameter(index)
        sample_aperture = self.get_sample_aperture_size()
        l2 = self.get_sample_aperture_to_detector_distance()  # Question why do we no longer need aperture offset
        l_beam_stop = 20.1 + 1.61 * bs_diam  # distance in cm from beam stop to anode plane (empirical calculation)
        return bs_diam + (bs_diam + sample_aperture) * l_beam_stop / (l2 - l_beam_stop)  # Return in cm

    def calculate_sample_to_detector_distance(self, index=0):
        """ Calculates the SDD(Sample to Detector Distance) value

        :param index: The index in the detector array
        :return: the SDD value that was just calculated
        :rtype: float
        """
        try:
            detector = self.detectors[index]
        except IndexError:
            detector = self.detectors[0]
        detector.sdd = self.collimation.detector_distance + self.collimation.space_offset
        return detector

    # Various class updaters
    def update_wavelength(self):
        """Runs the wavelength function that calculates the wavelength range

        :return: Nothing as it just runs a function
        :rtype: None
        """
        self.wavelength.calculate_wavelength_range()

    # Various class getter functions
    # Use these to be sure units are correct

    def calculate_slicer(self, index=0):
        """ Creates a dictionary of slicer parameter

        :param index: The index in the detector array
        :return: It returns nothing as the parameters it calculates are referenced in the return
        :rtype: None
        """
        slicer_params = self.slicer_params if self.slicer_params else {}

        self.detectors[index].calculate_all_beam_centers()
        slicer_params["x_center"] = self.detectors[index].beam_center_x
        slicer_params["y_center"] = self.detectors[index].beam_center_y
        slicer_params["pixel_size"] = self.detectors[index].pixel_size_x
        slicer_params["lambda_val"] = self.get_wavelength()
        slicer_params["detector_distance"] = self.get_sample_aperture_to_detector_distance(index)

        slicer_params["lambda_width"] = self.get_wavelength_spread()
        slicer_params["guides"] = self.get_number_of_guides()
        slicer_params["lens"] = self.collimation.guides.lenses if hasattr(self.collimation, 'guides') else None
        # QUESTION      Is it get_source_aperture_size or get_source_aperture the javascript defines sourceAperture
        # and sampleAperture differently
        slicer_params["source_aperture"] = self.get_source_aperture_size()
        slicer_params["sample_aperture"] = self.get_sample_aperture_size()
        slicer_params["beam_stop_size"] = self.data.calculated_beam_stop_diameter if self.data else self.get_beam_stop_diameter()
        slicer_params["SSD"] = self.get_source_to_sample_aperture_distance()
        slicer_params["SDD"] = self.get_sample_to_detector_distance()
        averaging_type = self.averaging_type
        match averaging_type:
            case "sector":
                self.slicer.insert(index, Sector(slicer_params))
            case "rectangular":
                self.slicer.insert(index, Rectangular(slicer_params))
            case "elliptical":
                self.slicer.insert(index, Elliptical(slicer_params))
            case "circular" | _:
                self.slicer.insert(index, Circular(slicer_params))

    def get_attenuation_factor(self):
        """ Gets the attenuation factor

        :return: The result of calculate attenuation factor
        :rtype: Float
        """
        return self.wavelength.attenuation_factor

    def get_attenuator_number(self):
        """Runs the calculation for attenuator number

        :return: The result of the calculate attenuator number
        :rtype: Int
        """

        # Number of attenuators in the beam
        return self.wavelength.number_of_attenuators

    def get_beam_flux(self):
        """ Gets the beam flux value from the data class

        :return: Returns the value of the
        :rtype: int
        """
        # Beam flux in cm^-2-s^-1
        self.data.calculate_beam_flux()
        return self.data.flux

    def get_beam_diameter(self, index=0):
        """ Gets the beam diameter value from the bea stops class at the specified index

        :param index: The index in the beam stops array
        :return: Returns the value of the beam diameter
        :rtype: int
        """
        # Beam diameter in centimeters
        return self.data.beam_diameter

    def get_beam_stop_diameter(self, index=0):
        """ Gets the beam stop diameter value from the beam stops class at the specified index

        :param index: The index in the beam stops array
        :return: Returns the value of the beam stop diameter
        :rtype: int
        """
        # Beam stop diameter in inches
        return self.beam_stops[index].beam_stop_diameter

    def get_number_of_guides(self):
        """Gets the value for the number of guides from the collimation class

        :return: the int value of the guides
        :rtype: Int
        """

        # Number of neutron guides in the beam
        guides = self.collimation.guides.number_of_guides
        if guides == "LENS":
            guides = 0
        else:
            guides = int(guides)
        return guides

    def get_sample_aperture_size(self):
        """The sample aperture radius from the collimation clas

        :return: The float value for the sample aperture size(Radius)
        :rtype: Float
        """
        # Sample Aperture radius in centimeters
        return self.collimation.get_sample_aperture_radius()

    def get_source_aperture_size(self):
        """The source aperture radius from the collimation clas

        :return: The float value for the source aperture size(Radius)
        :rtype: Float
        """
        # Source Aperture radius in centimeters
        return self.collimation.get_source_aperture_radius()

    def get_sample_aperture_diam(self):
        """The sample aperture diameter from the collimation clas

        :return: The float value for the sample aperture size(Diameter)
        :rtype: Float
        """
        # Sample Aperture diameter in centimeters
        return self.collimation.get_sample_aperture_diameter()

    def get_source_aperture_diam(self):
        """The source aperture diameter from the collimation clas

        :return: The float value for the source aperture size(Diameter)
        :rtype: Float
        """
        # Source Aperture diameter in centimeters
        return self.collimation.get_source_aperture_diameter()

    def get_sample_aperture_to_detector_distance(self, index=0):
        """The sample aperture to detector distance value from the detector class

        :param index: The index in the beam stops array
        :return: The float value of the SADD value
        :rtype: Float
        """
        # SADD in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            print("IndexError")
            return 0.0
        return detector.get_sadd()

    def get_sample_aperture_offset(self):
        """Gets the sample aperture offset from the collimation class

        :return: The float value of the sample aperture offset
        :rtype: Float
        """
        return self.collimation.get_sample_aperture_offset()

    def get_sample_to_detector_distance(self, index=0):
        """Gets the sample to detector distance from the detector class

        :param index: The index in the beam stops array
        :return: The float value of the sdd
        :rtype: Float
        """
        # SDD in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_sdd()

    def get_detector_offset(self, index=0):
        """Gets the detector offset from the detector class

        :param index: The index in the beam stops array
        :return: The float value of the detector offset
        :rtype: Float
        """
        # Detector offset in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_offset()

    def get_source_to_sample_distance(self):
        """Gets the source to sample distance from the collimation class

        :return: The float value of the ssd
        :rtype: Float
        """
        # SSD in centimeters
        return self.collimation.get_ssd()

    def get_source_to_sample_aperture_distance(self):
        """Gets the source to sample aperture distance from the collimation class

        :return: The float value of the ssad
        :rtype: Float
        """
        # SSAD in centimeters
        return self.collimation.get_ssad()

    def get_wavelength(self):
        """Gets the wavelength value from the wavelength class

        :return: The float value of the wavelength in angstroms
        :rtype: Float
        """
        # Wavelength in Angstroms
        return self.wavelength.get_wavelength()

    def get_wavelength_spread(self):
        """Gets the wavelength spread from the wavelength class

        :return: The float value of the wavelength spread
        :rtype: Float
        """
        # Wavelength spread in percent
        return self.wavelength.wavelength_spread

    def calculate_source_to_sample_aperture_distance(self):
        """Calculates and returns the source to sample aperture distance

        :return: The float value of the SSAD
        :rtype: Float
        """
        return self.collimation.calculate_source_to_sample_aperture_distance()
