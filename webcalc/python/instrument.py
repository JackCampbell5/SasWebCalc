import math
import numpy as np

from .units import Converter
from .constants import Constants
from .slicers import Circular
from .slicers import Sector
from .slicers import Rectangular
from .slicers import Elliptical


# TODO: Replace all nodes with Instrument parameters
# TODO: Call slicer directly using known parameters


def calculate_instrument(instrument, params):
    # type: (str, dict) -> dict
    """ The base calculation script. Creates an instrument class, calculates the instrumental resolution for the
    configuration, and returns two list of intensities
    Args:
        instrument: String defining instrument name
        params: Dictionary containing the following information:
            {
                instrument: "Name",
                wavelength:
                {
                    lambda: <value>,
                    lambda_unit: <unit>,
                    d_lambda: <value>,
                    d_lambda_unit: <unit>,
                    attenuation_factor: <value>
                },
                collimation:
                {
                    source_aperture: <value>,  # Source aperture radius
                    source_aperture_unit: "unit",  # Unit string for source aperture radius (e.g. mm, cm, centimeters)
                    ssd: <value>,  # Source to sample distance
                    ssd_unit: "unit",
                    ssad: <value>, # Source to sample aperture distance
                    ssad_unit: "unit",
                    sample_aperture: <value>,
                    sample_aperture_units: "unit",
                },
                detectors:
                [
                    {
                        sdd: <value>,
                        sdd_units: "unit",
                        sadd: <value>,
                        sadd_units: "unit",
                        offset: <value>,
                        offset_unit: "unit",
                        pixel_size_x: <value>,
                        pixel_size_x_unit: "unit"
                        pixel_size_y: <value>,
                        pixel_size_y_unit: "unit"
                        pixel_size_z: <value>,
                        pixel_size_z_unit: "unit"
                        pixels_x: <value>,
                        pixels_y: <value>,
                        pixels_z: <value>,
                        dead_time: <value>
                    },
                    ...,
                    {}
                ],
                constants:
                {

                }
            }

    Returns: [[1D resolutions], [2D resolutions]]
    """
    # TODO: Create classes for all instruments
    # i_class is the python object for the interment
    if instrument == 'ng7':
        # Creates NG7SANS object if instrument is ng7
        i_class = NG7SANS(instrument, params)
    elif instrument == 'ngb30':
        # Creates NG7SANS object if instrument is ngb30
        i_class = NGB30SANS(instrument, params)
    elif instrument == 'ngb10':
        # Creates NG7SANS object if instrument is ngb30
        i_class = NGB10SANS(instrument, params)
    else:
        i_class = Instrument(instrument, params)
    return i_class.sas_calc()


def set_params(instance, params):
    # type: (Instrument|Detector|Collimation, dict) -> None
    """
    Set class attributes based on a dictionary of values. The dict should map <param_name> -> <value>.
    Args:
        instance: An instance of any class type in this file that needs params set in bulk.
        params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
    Returns: None
    """
    if isinstance(params, (list, tuple)):
        # If a list is passed, try using the first value in the list
        params = params[0]
    if not isinstance(params, dict):
        # Retain existing attributes if params are not formatted properly
        print(f"Parameters of type {type(params)} are not allowed when setting params. Please pass a dictionary.")
        return
    for key, value in params.items():
        if hasattr(instance, key):
            # Set known attributes
            setattr(instance, key, value)
        else:
            # Print unrecognized attributes to the console
            print(f"The parameter {key} is not a known {instance} attribute. Unable to set it to {value}.")


class Aperture:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating collimation related data.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.diameter = 0.0
        self.diameter_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)

    def get_diameter(self):
        return self.parent.d_converter(self.diameter, self.diameter_unit)

    def get_radius(self):
        return self.parent.d_converter(self.diameter / 2, self.diameter_unit)

    def get_offset(self):
        return self.parent.d_converter(self.offset, self.offset_unit)


class BeamStop:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating collimation related data.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.diameter = 0.0
        self.diameter_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.beam_stop_size = 0.0
        self.beam_stop_diameter = 0.0
        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)


class Collimation:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating collimation related data.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.source_aperture = Aperture(parent, params.get('source_aperture', {}))
        self.sample_aperture = Aperture(parent, params.get('sample_aperture', {}))
        self.guides = Guide(parent, params.get('guides', {}))
        # Sets the params array to main values without aperture array
        params = params['0']
        self.ssd = 0.0
        self.ssd_unit = 'cm'
        self.ssad = 0.0
        self.ssad_unit = 'cm'
        self.sample_space = " "
        self.aperture_offset = 0.0
        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)
        self.calculate_source_to_sample_aperture_distance()

    def get_source_aperture_radius(self):
        return self.source_aperture.get_radius()

    def get_source_aperture_diameter(self):
        return self.source_aperture.get_diameter()

    def get_sample_aperture_radius(self):
        return self.sample_aperture.get_radius()

    def get_sample_aperture_diameter(self):
        return self.sample_aperture.get_diameter()

    def get_ssd(self):
        return self.parent.d_converter(self.ssd, self.ssd_unit)

    def get_ssad(self):
        return self.parent.d_converter(self.ssad, self.ssad_unit)

    def get_sample_aperture_offset(self):
        return self.sample_aperture.get_offset()

    def calculate_source_to_sample_aperture_distance(self):
        self.ssad = (self.guides.get_maximum_length() - self.guides.get_maximum_length()
                     * self.guides.number_of_guides - self.get_sample_aperture_offset())


class Detector:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating detector related data.
        Most useful for instrument with multiple detectors.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.sadd = 0.0
        self.sadd_unit = 'cm'
        self.sdd = 0.0
        self.sdd_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.pixel_size_x = 0.0  # aPixel in constants.js
        self.pixel_size_x_unit = 'cm'
        self.pixel_size_y = 0.0
        self.pixel_size_y_unit = 'cm'
        self.pixel_size_z = 0.0
        self.pixel_size_z_unit = 'cm'
        self.pixel_no_x = 0
        self.pixel_no_y = 0
        self.pixel_no_z = 0
        self.per_pixel_max_flux = 1e40
        self.dead_time = 0
        self.beam_center_x = 0.0
        self.beam_center_y = 0.0
        self.beam_center_z = 0.0
        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)
        # Calculate all beam centers using existing values
        self.calculate_all_beam_centers()

    def calculate_all_beam_centers(self):
        self.calculate_beam_center_x()
        self.calculate_beam_center_y()
        self.calculate_beam_center_z()

    def calculate_beam_center_x(self):
        # Find the number of x pixels in the detector
        x_pixels = self.pixel_no_x
        # Get pixel size in mm and convert to cm
        dr = self.get_pixel_size_x()
        # Get detector offset in cm
        offset = self.get_offset()
        self.beam_center_x = x_pixels / 2 + 0.5 if dr == 0 else offset / dr + x_pixels / 2 + 0.5

    def calculate_beam_center_y(self):
        # Find the number of y pixels in the detector
        y_pixels = self.pixel_no_y
        # Get detector offset in cm
        self.beam_center_y = y_pixels / 2 + 0.5

    def calculate_beam_center_z(self):
        # Find the number of x pixels in the detector
        z_pixels = self.pixel_no_z
        # Get detector offset in cm
        self.beam_center_z = z_pixels / 2 + 0.5

    def get_pixel_size_x(self):
        return self.parent.d_converter(self.pixel_size_x, self.pixel_size_x_unit)

    def get_pixel_size_y(self):
        return self.parent.d_converter(self.pixel_size_y, self.pixel_size_y_unit)

    def get_pixel_size_z(self):
        return self.parent.d_converter(self.pixel_size_z, self.pixel_size_z_unit)

    def get_ssd(self):
        return self.parent.d_converter(self.sdd, self.sdd_unit)

    def get_sadd(self):
        return self.parent.d_converter(self.sadd, self.sadd_unit)

    def get_offset(self):
        return self.parent.d_converter(self.offset, self.offset_unit)

    def calculate_distance_from_beam_center(self, coefficient):
        pixel_array = np.array(self.pixel_no_x, self.pixel_no_y)
        # FIXME: This should be more than just pixel size in x
        raw_value = pixel_array * self.get_pixel_size_x()
        return coefficient * math.tan((raw_value / coefficient))


class Guide:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating detector related data.
        Most useful for instrument with multiple detectors.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        # TODO  J   Import values for  guide_width, gap_at_start, and length_per_guide
        self.parent = parent
        self.guide_width = 0.0  ##
        self.guide_width_unit = 'cm'
        self.transmission_per_guide = 1.0  ## GuideLoss
        self.length_per_guide = 0.0
        self.length_per_guide_unit = 'cm'
        self.number_of_guides = 0
        self.lenses = False
        self.gap_at_start = 0.0
        self.gap_at_start_unit = 'cm'
        self.maximum_length = 0.0
        self.maximum_length_unit = 'cm'

        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)

    def get_gap_at_start(self):
        return self.parent.d_converter(self.gap_at_start, self.gap_at_start_unit)

    def get_guide_width(self):
        return self.parent.d_converter(self.guide_width, self.guide_width_unit)

    def get_length_per_guide(self):
        return self.parent.d_converter(self.length_per_guide, self.length_per_guide_unit)

    def get_maximum_length(self):
        return self.parent.d_converter(self.maximum_length, self.maximum_length_unit)


class Wavelength:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating collimation related data.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.wavelength = 0.0
        self.wavelength_min = 0.0
        self.wavelength_max = np.inf
        self.wavelength_unit = 'nm'
        self.wavelength_spread = 0.0
        self.wavelength_spread_unit = '%'
        self.wavelength_constants = (0.0, 0.0)
        self.rpm_range = (0.0, np.inf)
        self.number_of_attenuators = 0
        self.attenuation_factor = 0
        self.d_converter = Converter(self.wavelength_unit)
        # TODO Create WavelengthCalculator class and implement object
        # self.d_lambda_allowed = WavelengthCalculator...

        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)
        self.calculate_wavelength_range()

    def get_wavelength(self):
        return self.parent.d_converter(self.wavelength, self.wavelength_unit)

    def set_wavelength(self, value, units):
        self.wavelength = self.d_converter(value, units)

    def calculate_wavelength_range(self):
        try:
            calculated_min = self.wavelength_constants[0] + (self.wavelength_constants[1] / self.rpm_range[1])
        except ZeroDivisionError:
            calculated_min = 0.0
        self.wavelength_min = calculated_min if calculated_min > self.wavelength_min else self.wavelength_min
        try:
            calculated_max = self.wavelength_constants[0] + (self.wavelength_constants[1] / self.rpm_range[0])
        except ZeroDivisionError:
            calculated_max = np.Inf
        self.wavelength_max = calculated_max if calculated_max < self.wavelength_max else self.wavelength_max


class Data:
    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """
        A class for storing and manipulating collimation related data.
        Args:
            parent: The Instrument instance this Detector is a part of
            params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.peak_flux = np.inf  # peakFlux in constants.js
        self.peak_wavelength = 0.0  # peakLambda in constants.js
        self.bs_factor = 0.0  # BSFactor in constants.js
        self.trans_1 = 0.0
        self.trans_2 = 0.0
        self.trans_3 = 0.0
        self.beta = 0.0  # b in constants
        self.charlie = 0.0  # c in constants
        self.q_max = 6.0
        self.q_max_horizon = 6.0
        self.q_max_vert = 6.0
        self.q_unit = '1/A'
        self.q_min = 0.0
        self.q_values = []
        self.intensity = []
        # Flux should be in cm^-2*s^-1
        self.flux = 0.0
        self.flux_size_unit = 'cm'
        self.flux_time_unit = 's'
        self.set_params(params)

    def set_params(self, params=None):
        # type: (dict) -> None
        """
        Set class attributes based on a dictionary of values using the generic set_params function.
        Args:
            params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        Returns: None
        """
        set_params(self, params)

    def calculate_beam_flux(self):
        # FIXME: Flux calculation is about 7x too high
        guide_loss = self.parent.collimation.guides.transmission_per_guide
        sample_aperture = self.parent.get_sample_aperture_size()
        sdd = self.parent.get_sample_to_detector_distance()
        wave = self.parent.get_wavelength()
        lambda_spread = self.parent.get_wavelength_spread()
        guides = self.parent.get_number_of_guides()

        # Run calculations
        alpha = (self.parent.get_source_aperture_size() + sample_aperture) / (2 * sdd)
        f = (self.parent.collimation.guides.get_gap_at_start() * alpha) / (
                2 * self.parent.collimation.guides.get_guide_width())
        trans4 = (1 - f) * (1 - f)
        trans5 = math.exp(guides * math.log(guide_loss))
        trans6 = 1 - wave * (self.beta - (guides / 8) * (self.beta - self.charlie))
        total_trans = self.trans_1 * self.trans_2 * self.trans_3 * trans4 * trans5 * trans6

        area = math.pi * sample_aperture * sample_aperture / 4
        d2_phi = self.peak_flux / (2 * math.pi)
        d2_phi = d2_phi * math.exp(4 * math.log(self.peak_wavelength / wave))
        d2_phi = d2_phi * math.exp(-1 * math.pow(self.peak_wavelength / wave, 2))
        solid_angle = (math.pi / 4) * (sample_aperture / sdd) * (sample_aperture / sdd)
        self.flux = area * d2_phi * lambda_spread * solid_angle * total_trans

    def calculate_min_and_max_q(self, index=0):
        sdd = self.parent.get_sample_to_detector_distance()
        offset = self.parent.get_detector_offset()
        wave = self.parent.get_wavelength()
        pixel_size = self.parent.detectors[index].get_pixel_size_x()
        det_width = pixel_size * self.parent.detectors[index].pixel_no_x
        bs_projection = self.parent.calculate_beam_stop_projection()
        # Calculate Q-maximum and populate the page
        radial = math.sqrt(math.pow(0.5 * det_width, 2) + math.pow((0.5 * det_width) + offset, 2))
        self.q_max = 4 * (math.pi / wave) * math.sin(0.5 * math.atan(radial / sdd))
        # Calculate Q-minimum and populate the page
        self.q_min = (math.pi / wave) * (bs_projection + pixel_size + pixel_size) / sdd
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) + offset) / sdd)
        self.q_max_horizon = 4 * (math.pi / wave) * math.sin(0.5 * theta)
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) / sdd))
        self.q_max_vert = 4 * (math.pi / wave) * math.sin(0.5 * theta)

    def get_beam_flux(self):
        self.calculate_beam_flux()
        return (math.pow(self.parent.d_converter(self.flux, self.flux_size_unit), 2)
                * self.parent.t_converter(self.flux, self.flux_time_unit))


class Instrument:
    isReal = False

    def __init__(self, name="", params=None):
        # Unit converters
        self.slicer = None
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.data = None
        self.collimation = None
        self.wavelength = None
        self.detectors = None
        self.beam_stops = None
        if not params:
            params = {}
            # Only store values used for calculations in Instrument class
            self.name = name
        self.constants = Constants()
        self.load_params(params)

    """
        Pseudo-abstract method to initialize constants associated with an instrument
    """

    def load_params(self, params):
        print("Default Load Params")
        self.load_objects(params)
        # default values for default instruments

    def load_objects(self, params):
        # Creates the objects with the param array
        #       (This is not a part of load params so instrument can have default values if necessary)

        self.beam_stops = params.get('beam_stops', [{'beam_stop_diameter': 1.0, 'beam_diameter': 1.0}])
        # TODO Implement current_beamstop object
        self.detectors = [Detector(self, detector_params) for detector_params in params.get('detectors', [{}])]
        self.collimation = Collimation(self, params.get('collimation', {}))
        self.wavelength = Wavelength(self, params.get('wavelength', {}))
        # TODO   What class should be imported into data
        self.data = Data(self, params.get('data', {}))

        # gets the parmaters for slicer object and updates the parameters dictionary for that
        params["slicer"] = self.get_slicer_params(params.get('slicer', {}))

        # Creates slicer objects
        averaging_type = params.get("average_type", "ERROR")
        if averaging_type == "sector":
            self.slicer = Sector(params.get('slicer', {}))
        elif averaging_type == "rectangular":
            self.slicer = Rectangular(params.get('slicer', {}))
        elif averaging_type == "elliptical":
            self.slicer = Elliptical(params.get('slicer', {}))
        else:
            self.slicer = Circular(params.get('slicer', {}))

        # TODO move this function to sas_calc function
        self.slicer.calculate_q_range_slicer()

    def sas_calc(self):
        # MainFunction for this class

        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculate_instrument_parameters()

        # Final output returned to the JS
        # FIXME: What values need to be returned?
        # TODO Return Values
        return "Return Works"

    def calculate_instrument_parameters(self):
        # Calculate the beam stop diameter
        self.calculate_beam_stop_diameter()
        # Calculate the estimated beam flux
        self.data.calculate_beam_flux()
        # Calculate the figure of merit
        self.calculate_figure_of_merit()
        # Calculate the number of attenuators
        self.calculate_attenuators()
        # Do Circular Average of an array of 1s

        # TODO Figure out point of this
        # for index in range(len(self.detectors) - 1):
        #     self.data.calculate_min_and_max_q(index)
        #     # TODO: This might not be needed here...
        #     # TODO J    This method does not exist
        #     self.slicer.calculate_q_range_slicer(index)

    def calculate_attenuation_factor(self, index=0):
        a2 = self.get_sample_aperture_size()
        beam_diam = self.get_beam_diameter(index)
        a_pixel = self.detectors[index].get_pixel_size_x()
        i_pixel_max = self.detectors[index].per_pixel_max_flux
        num_pixels = (math.pi / 4) * (0.5 * (a2 + beam_diam) / a_pixel) ** 2
        i_pixel = self.get_beam_flux() / num_pixels
        atten = 1.0 if i_pixel < i_pixel_max else i_pixel_max / i_pixel
        # Question .toNumeric what???
        self.wavelength.attenuation_factor = atten if atten == 1.0 else int(atten)

    def calculate_attenuators(self):
        self.calculate_attenuation_factor()
        atten = self.get_attenuation_factor()
        af = 0.498 + 0.0792 * self.get_wavelength() - 1.66e-3 * self.get_wavelength() ** 2
        nf = -1 * math.log(atten) / af
        num_atten = math.ceil(nf)
        if num_atten > 6:
            num_atten = 7 + math.floor((num_atten - 6) / 2)
        self.wavelength.number_of_attenuators = num_atten

    def calculate_beam_diameter(self, index=0, direction='maximum'):
        # Update all instrument calculations needed for beam diameter
        self.collimation.get_ssad()
        self.get_sample_to_detector_distance(index)
        # Get instrumental values
        source_aperture = self.get_source_aperture_size()
        sample_aperture = self.get_sample_aperture_size()
        ssd = self.get_source_to_sample_aperture_distance()
        sdd = self.get_sample_aperture_to_detector_distance(index)
        wavelength = self.get_wavelength()
        wavelength_spread = self.get_wavelength_spread()
        if self.collimation.guides.lenses:
            # If LENS configuration, the beam size is the source aperture size
            # FIXME: This is showing -58 cm... Why?!?!
            self.beam_stops[index]["beam_stop_diameter"] = self.get_source_aperture_size()
        # Calculate beam width on the detector
        try:
            beam_width = source_aperture * sdd / ssd + sample_aperture * (ssd + sdd) / ssd
        except ZeroDivisionError:
            beam_width = 0.0
        # Beam height due to gravity
        bv3 = ((ssd + sdd) * sdd) * wavelength ** 2
        bv4 = bv3 * wavelength_spread
        bv = beam_width + 0.0000125 * bv4
        # Larger of the width*safetyFactor and height
        bm_bs = self.data.bs_factor * beam_width
        bm = bm_bs if bm_bs > bv else bv
        if direction == 'vertical':
            beam_diam = bv
        elif direction == 'horizontal':
            beam_diam = bm_bs
        else:
            beam_diam = bm
        self.beam_stops[index]["beam_diameter"] = beam_diam

    def calculate_beam_stop_diameter(self, index=0):
        self.calculate_beam_diameter(index, 'maximum')
        beam_diam = self.get_beam_diameter(index)
        for i in self.beam_stops:
            beam_stop_dict = i
            if beam_stop_dict.get("beam_stop_diameter") >= beam_diam:
                self.beam_stops[index]["beam_stop_diameter"] = beam_stop_dict["beam_stop_diameter"]
                return
        else:
            # If this is reached, that means the beam diameter is larger than the largest known beam stop
            self.beam_stops[index].beam_stop_diameter = self.beam_stops[len(self.beam_stops) - 1].beam_stop_diameter

    def calculate_beam_stop_projection(self, index=0):
        self.get_sample_to_detector_distance(index)
        self.calculate_beam_diameter(index)
        self.calculate_beam_stop_diameter(index)
        bs_diam = self.get_beam_stop_diameter(index)
        sample_aperture = self.get_sample_aperture_size()
        l2 = self.get_sample_aperture_to_detector_distance()  # Question why do we no longer need apature offset
        l_beam_stop = 20.1 + 1.61 * self.get_beam_stop_diameter()  # distance in cm from beam stop to anode plane
        return bs_diam + (bs_diam + sample_aperture) * l_beam_stop / (l2 - l_beam_stop)  # Return in cm

    def calculate_figure_of_merit(self):
        figure_of_merit = math.pow(self.get_wavelength(), 2) * self.get_beam_flux()
        # Question what is the .toNumeric Method?
        return int(figure_of_merit)

    def calculate_source_to_sample_aperture_distance(self, index=0):
        # Get the number of guides
        nGds = self.collimation.guides.number_of_guides
        # Get the source to sample distence node
        SSD = self.collimation.ssd
        # Get the sample location
        sample_space = self.collimation.sample_space
        ssd = 0.0
        ssd_offset = 0  # Import constants
        aperture_offset = self.collimation.aperture_offset
        # TODO import constants for offset based on sample space

    def calculate_sample_to_detector_distance(self):
        pass

    # Various class updaters
    def update_wavelength(self, run_sas_calc=True):
        self.wavelength.calculate_wavelength_range()
        if run_sas_calc:
            self.sas_calc()

    # Various class getter functions
    # Use these to be sure units are correct

    def get_slicer_params(self, slicer_params, index=0):
        # Import averaging_params
        averaging_params = slicer_params.get("averaging_params", [])
        slicer_params["phi"] = (math.pi / 180) * averaging_params[0]
        slicer_params["d_phi"] = (math.pi / 180) * averaging_params[1]
        slicer_params["detector_sections"] = averaging_params[2]
        slicer_params["q_center"] = averaging_params[3]
        slicer_params["q_width"] = averaging_params[4]
        slicer_params["aspect_ratio"] = averaging_params[5]

        # Import params needed for calculateQRangeSlicer
        #  aperture_offset, coeff, x_pixels, y_pixels imported in object creation

        # QUESTION      [0] Do I need to run a loop here? how does this work with multiple detectors
        self.detectors[index].calculate_beam_center_x()
        self.detectors[index].calculate_beam_center_y()
        slicer_params["x_center"] = self.detectors[index].beam_center_x
        slicer_params["y_center"] = self.detectors[index].beam_center_y
        slicer_params["pixel_size"] = self.detectors[index].pixel_size_x
        slicer_params["lambda_val"] = self.wavelength.get_wavelength()
        slicer_params["detector_distance"] = self.detectors[index].get_ssd()

        slicer_params["lambda_width"] = self.wavelength.wavelength_spread
        slicer_params["guides"] = self.collimation.guides.number_of_guides
        # QUESTION      Is it get_source_aperture_size or get_source_aperture the javascript defines sourceAperture
        # and sampleAperture differently
        slicer_params["source_aperture"] = self.get_source_aperture_size() * 0.5
        slicer_params["sample_aperture"] = self.get_sample_aperture_size() * 0.5
        slicer_params["beam_stop_size"] = self.get_beam_stop_diameter() * 2.54
        slicer_params["SSD"] = self.calculate_source_to_sample_aperture_distance()
        slicer_params["SDD"] = self.calculate_sample_to_detector_distance()
        del slicer_params["averaging_params"]
        return slicer_params

    def get_attenuation_factor(self):
        # TODO Fix The attenuation factor value calculated based on the number of attenuators
        # Fixed ish this is will just infinatly loop
        return self.wavelength.attenuation_factor

    def get_attenuators(self):
        # Number of attenuators in the beam
        return self.calculate_attenuators()

    def get_beam_flux(self):
        # Beam flux in cm^-2-s^-1
        return self.data.get_beam_flux()

    def get_beam_diameter(self, index=0):
        # Beam diameter in centimeters
        return self.beam_stops[index].get("beam_diameter")

    def get_beam_stop_diameter(self, index=0):
        # Beam stop diameter in inches
        # TODO: Convert to centimeters
        return self.beam_stops[index]["beam_stop_diameter"]

    def get_number_of_guides(self):
        # Number of neutron guides in the beam
        guides = self.collimation.guides.number_of_guides
        if guides == "LENS":
            guides = 0
        else:
            guides = int(guides)
        return guides

    def get_sample_aperture_size(self):
        # Sample Aperture radius in centimeters
        return self.collimation.get_sample_aperture_radius()

    def get_source_aperture_size(self):
        # Source Aperture radius in centimeters
        return self.collimation.get_source_aperture_radius()

    def get_sample_aperture_to_detector_distance(self, index=0):
        # SADD in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_sadd()

    def get_sample_aperture_offset(self):
        return self.collimation.get_sample_aperture_offset()

    def get_sample_to_detector_distance(self, index=0):
        # SDD in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_ssd()

    def get_detector_offset(self, index=0):
        # Detector offset in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_offset()

    def get_source_to_sample_distance(self):
        # SSD in centimeters
        return self.collimation.get_ssd()

    def get_source_to_sample_aperture_distance(self):
        # SSAD in centimeters
        return self.collimation.get_ssad()

    def get_wavelength(self):
        # Wavelength in Angstroms
        return self.wavelength.get_wavelength()

    def get_wavelength_spread(self):
        # Wavelength spread in percent
        return self.wavelength.wavelength_spread


class NG7SANS(Instrument):

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        # Super is the Instrument class
        super().__init__(name, params)

    def load_params(self, params):
        print("NG7SANS Load Params")
        params["collimation"]["guides"]["gap_at_start"] = 188
        params["collimation"]["guides"]["guide_width"] = 5
        params["collimation"]["guides"]["transmission_per_guide"] = 0.974
        params["data"] = {}
        params["data"]["bs_factor"] = 1.05
        params["detectors"][0]["per_pixel_max_flux"] = 100
        params["data"]["peak_flux"] = 25500000000000
        params["data"]["peak_wavelength"] = 5.5
        params["data"]["beta"] = 0.0395
        params["data"]["charlie"] = 0.0442
        params["data"]["trans_1"] = 0.63
        params["data"]["trans_2"] = 0.7
        params["data"]["trans_3"] = 0.75
        params["detectors"][0]["pixel_size_x"] = 5.08
        params["slicer"]["aperture_offset"] = 5.0
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "ng7sans.ncnr.nist.gov"
        params["temp"]["HuberOffset"] = 54.8
        params["temp"]["ChamberOffset"] = 0.0

        super().load_objects(params)


class NGB30SANS(Instrument):
    # Class for the NGB 30m SANS instrument
    def __init__(self, name, params):
        super().__init__(name, params)

    def load_params(self, params):
        print("NGB30SANS Load Params")
        params["data"] = {}
        params["data"]["bs_factor"] = 1.05
        params["detectors"][0]["per_pixel_max_flux"] = 100.0
        params["data"]["peak_flux"] = 2.42e13
        params["data"]["peak_wavelength"] = 5.5
        params["data"]["beta"] = 0.0
        params["data"]["charlie"] = -0.0243
        params["data"]["trans_1"] = 0.63
        params["data"]["trans_2"] = 1.0
        params["data"]["trans_3"] = 0.75
        params["detectors"][0]["pixel_size_x"] = 5.08
        params["collimation"]["guides"]["gap_at_start"] = 100
        params["collimation"]["guides"]["guide_width"] = 6.0
        params["collimation"]["guides"]["transmission_per_guide"] = 0.924
        params["slicer"]["aperture_offset"] = 5
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "ngb30sans.ncnr.nist.gov"
        params["temp"]["HuberOffset"] = 54.8
        params["temp"]["ChamberOffset"] = 0.0

        super().load_objects(params)


class NGB10SANS(Instrument):
    # Class for the NGB 10m SANS instrument
    def __init__(self, name, params):
        super().__init__(name, params)

    def load_params(self, params):
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
        params["detectors"][0]["pixel_size_x"] = 5.08
        params["collimation"]["guides"]["gap_at_start"] = 165
        params["collimation"]["guides"]["guide_width"] = 5
        params["collimation"]["guides"]["transmission_per_guide"] = 0.974
        params["slicer"]["aperture_offset"] = 5
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128

        # Temporary constants not in use anymore
        params["temp"] = {}
        params["temp"]["serverName"] = "ngbsans.ncnr.nist.gov"
        params["temp"]["HuberOffset"] = 0.0
        params["temp"]["ChamberOffset"] = 0.0
        super().load_objects(params)

    def calculate_source_to_sample_aperture_distance(self):
        super(NGB10SANS, self).calculate_source_to_sample_aperture_distance()
        # TODO Implement object spesific function

# class VSANS(Instrument):
#     # Class for the VSANS instrument
#     def __init__(self, name, params):
#         super().__init__(name, params)
#
#     def load_params(self, params):
#         print("VSANS Load Params")
#         super().load_objects(params)
