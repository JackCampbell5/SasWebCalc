import math
import numpy as np
from typing import Union

from .units import Converter

NUMBER_TYPE = Union[float, int]
VALUE_TYPE = Union[NUMBER_TYPE, str]
CALC_TYPE = dict[str, Union[VALUE_TYPE, list[Union[VALUE_TYPE]]]]
PARAM_TYPE = dict[str, dict[str, Union[VALUE_TYPE]]]


def set_params(instance, params, float_params=None):
    """ Set class attributes based on a dictionary of values. The dict should map <param_name> -> <value>.


    :param instance: An instance of any class type in this file that needs params set in bulk.
    :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
    :param float_params: A list of parameters that are meant to be float
    :return: Nothing just prints errors if there are anu
    :rtype: None
    """
    if not float_params:
        float_params = []
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
            if value is not None:
                if key in float_params:
                    try:
                        value = float(value)
                    except ValueError:
                        # Bad value sent for floats -> raise error
                        raise
                    except Exception:
                        # Otherwise, ignore
                        pass
                setattr(instance, key, value)
        else:
            # Print unrecognized attributes to the console
            print(f"The parameter {key} is not a known {instance} attribute. Unable to set it to {value}.")


class Aperture:
    """A class for storing and manipulating Aperture data.

    :param Instrument self.parent: A parent object that has all the objects
    :param float self.diameter: Stores the diameter
    :param str self.diameter_unit: Stores the unit for the diameter value, used for converter
    :param float self.offset: How much the diameter is offset
    :param str self.offset_unit: The units of the offset used for converter
    """

    def __init__(self, parent, params, name=None):
        """Creates object parameters for BeamStop class and runs set params method
        Sets object parameters parent, diameter, diameter_unit, offset, and offset_unit

        :param  Instrument parent: The Collimation instance this Aperture object is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :returns: Nothing as it just sets all the parameters
        :rtype: None
        """
        self.parent = parent
        self.name = name
        self.diameter = 0.0
        self.diameter_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.set_params(params)

    def set_params(self, params=None):
        """
        Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        float_params = ["diameter", "offset"]
        set_params(self, params, float_params)
        if self.name == "sample_aperture":
            self.diameter *= 2.54

    def get_diameter(self):
        """ Gets diameter value of the Aperture object

        :returns: Converted diameter and diameter unit value for distance
        :rtype: int
        """
        return self.parent.d_converter(self.diameter, self.diameter_unit)

    def get_radius(self):
        """ Gets the radius of the Aperture object

        :returns: Converted radius and diameter unit value for distance
        :rtype: int
        """
        return self.parent.d_converter(self.diameter / 2, self.diameter_unit)

    def get_offset(self):
        """  Gets the offset of the Aperture object

        :returns: converted offset and offset unit value for distance
        :rtype: int
        """
        return self.parent.d_converter(self.offset, self.offset_unit)


class BeamStop:
    # TODO update documentation once class is implemented
    """ A class for storing and manipulating BeamStop related data.

    :param Instrument self.parent: The parent instrument object
    :param float self.diameter: The diameter of the beam(Calculated)
    :param str self.diameter_unit: The unit for diameter of the beam(Usually CM)
    :param float self.offset: The beam stop offset
    :param str self.offset_unit: The unit for the beam stop offset
    :param float self.beam_stop_size:  The size of the beam stop (Calculated)
    :param int self.beam_stop_diameter: The beam stop diameter
    """

    # TODO implement this class somewhere
    def __init__(self, parent, params):
        """Creates object parameters for BeamStop class and runs set params method
        Sets object parameters self.parent, self.diameter, self.diameter_unit, self.offset,
        self.offset_unit, self.beam_stop_size, and self.beam_stop_diameter

        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :return: None as it just sets the parameters
        :rtype: None
        """
        # TODO Figure out how many of these parameters are Actually necessary
        self.parent = parent
        self._beam_stop_diameter = 0.0
        self.set_params(params)

    def set_params(self, params=None):
        """
        Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :return: None as it just sets the parameters
        :rtype: None
        """
        float_params = ["diameter", "offset", "beam_stop_size", "beam_stop_diameter"]
        set_params(self, params, float_params)

    @property
    def beam_stop_diameter(self):
        return self._beam_stop_diameter

    @beam_stop_diameter.setter
    def beam_stop_diameter(self, value):
        self._beam_stop_diameter = value


class Collimation:
    """A class for storing and manipulating Collimation related data.

    :param  Instrument self.parent: The parent instrument object
    :param  Aperture self.source_aperture: An aperture object for source aperture(Passed source aperture parameters)
    :param  Aperture self.sample_aperture: An Aperture object for the sample aperture(Passed sample aperture parameters)
    :param  Guide self.guides: A guide object that contains the guide values(Passed the guide parameters)
    :param  float self.ssd: The source to sample distance
    :param  str self.ssd_unit: The unit of the source to sample distance
    :param  float self.ssad: The source to sample aperture distance
    :param  str self.ssad_unit: The unit of the source to sample aperture distance
    :param  float self.sample_space: The sample space chosen by the user (Chamber or Huber)
    :param  float self.aperture_offset: The offset if the aperture(Used for calculation of SSAD)
    :param  float self.space_offset: The offset given by the sample space
    :param  float self.detector_distance: The distance to the detector

    """

    def __init__(self, parent, params):
        # type: (Instrument, dict) -> None
        """Creates object parameters for Collimation class and runs set params method
        Sets object parameters self.parent, self.source_aperture, self.sample_aperture,
        self.guides, self.ssd, self.ssd_unit, self.ssad, self.ssad_unit, self.sample_space,
        self.aperture_offset, self.space_offset, and self.detector_distance

        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.source_aperture = Aperture(parent, params.pop('source_aperture', {}), name="source_aperture")
        self.sample_aperture = Aperture(parent, params.pop('sample_aperture', {}), name="sample_aperture")
        self.guides = Guide(parent, params.pop('guides', {}))
        # Sets the params array to main values without aperture array
        self.ssd = 0.0
        self.ssd_unit = 'cm'
        self.ssad = 0.0
        self.ssad_unit = 'cm'
        self.sample_space = " "
        self.aperture_offset = 0.0
        self.space_offset = 0.0
        self.detector_distance = 0.0
        self.set_params(params)

    def set_params(self, params=None):
        """
        Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :return: None as it just sets the parameters
        :rtype: None
        """
        float_params = ["ssd", "ssad", "aperture_offset", "space_offset", "detector_distance"]
        set_params(self, params, float_params)

    def get_source_aperture_radius(self):
        """ Gets the radius attribute from the Source Aperture object

        :return: The integer value of the radius
        :rtype: float
        """
        return self.source_aperture.get_radius()

    def get_source_aperture_diameter(self):
        """ The diameter attribute from the Source Aperture object

        :return: The integer value of the diameter
        :rtype: float
        """
        return self.source_aperture.get_diameter()

    def get_sample_aperture_radius(self):
        """Gets the radius attribute from the Sample Aperture object

        :return:The integer value of the radius
        :rtype: float
        """
        return self.sample_aperture.get_radius()

    def get_sample_aperture_diameter(self):
        """The diameter attribute from the Sample Aperture object

        :return: The integer value of the diameter
        :rtype: float
        """
        return self.sample_aperture.get_diameter()

    def get_ssd(self):
        """ The source to sample distance

        :return: The ssd value
        :rtype: float
        """
        return self.parent.d_converter(self.ssd, self.ssd_unit)

    def get_ssad(self):
        """ The source to sample aperture distance

        :return: The SSAD value
        :rtype: float
        """
        return self.parent.d_converter(self.ssad, self.ssad_unit)

    def get_sample_aperture_offset(self):
        """
        :return: The sample aperture offset
        :rtype: float
        """
        return self.sample_aperture.get_offset()

    def calculate_source_to_sample_distance(self):
        """ Calculates the source to sample distance from the ssad value and aperture offset value

        :return: The calculates SSD value
        :rtype: float
        """
        self.ssd = self.ssad - self.aperture_offset

    def calculate_source_to_sample_aperture_distance(self):
        """ Calculates the source to sample aperture distance from the guide values and sample aperture offset

        :return: The calculated SSAD value
        :rtype: float
        """
        self.ssad = (
                    self.guides.get_maximum_length() - self.guides.get_length_per_guide() * self.guides.number_of_guides - self.get_sample_aperture_offset())
        return self.ssad


class Detector:
    """A class for storing and manipulating Detector related data.

    :param  Instrument self.parent: The parent instrument object
    :param  float self.sadd: The source to aperture detector distance
    :param  str self.sadd_unit: The unit of the source to aperture detector distance(Typically centimeters)
    :param  float self.sdd: The source to detector distance
    :param  str self.sdd_unit: The unit of the source to detector distance(Typically centimeters)
    :param  float self.offset: The offset of the detector
    :param  str self.offset_unit: The offset of the detector(Typically centimeters)
    :param  float self.pixel_size_x: The size of the detector in the x direction
    :param  str self.pixel_size_x_unit: The unit for the size of the detector in the x direction (Typically centimeters)
    :param  float self.pixel_size_y: The size of the detector in the y direction
    :param  str self.pixel_size_y_unit: The unit for the size of the detector in the y direction (Typically centimeters)
    :param  float self.pixel_size_z: The size of the detector in the z direction
    :param  str self.pixel_size_z_unit: The unit for the size of the detector in the z direction (Typically centimeters)
    :param  float self.pixel_no_x: The number of pixels on the detector in the horizontal direction
    :param  float self.pixel_no_y: The number of pixels on the detector in the vertical direction
    :param  float self.pixel_no_z: The number of pixels on the detector along the beam direction
    :param  float self.per_pixel_max_flux: The maximum neutron flux each pixel can safely accept, in n/s
    :param  float self.dead_time: A time constant related to the minimum time between neutron interactions that
        the detector can properly interpret.
    :param  float self.beam_center_x: The location of the center of the beam in the x direction
    :param  float self.beam_center_y: The location of the center of the beam in the y direction
    :param  float self.beam_center_z: The location of the center of the beam in the z direction

    """

    def __init__(self, parent, params):
        """Creates object parameters for Detector class and runs set params method

        Most useful for instrument with multiple detectors.
        Sets object parameters self.parent, self.sadd, self.sadd_unit, self.sdd, self.sdd_unit, self.offset,
        self.offset_unit, self.pixel_size_x, self.pixel_size_x_unit, self.pixel_size_y, self.pixel_size_y_unit,
        self.pixel_size_z, self.pixel_size_z_unit, self.pixel_no_x, self.pixel_no_y, self.pixel_no_z,
        self.per_pixel_max_flux, self.dead_time, self.beam_center_x, self.beam_center_y, and self.beam_center_z

        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :return: None as it just sets the parameters
        :rtype: None
        """
        self.parent = parent
        self.sadd = 0.0
        self.sadd_unit = 'cm'
        self.sdd = 0.0
        self.sdd_unit = 'cm'
        self.aperture_offset = 5.0
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.pixel_size_x = 0.0  # aPixel in constants.js
        self.pixel_size_x_unit = 'cm'
        self.pixel_size_y = 0.0
        self.pixel_size_y_unit = 'cm'
        self.pixel_size_z = 0.0
        self.pixel_size_z_unit = 'cm'
        # TODO import these as constants (128 is just temporary to make nice numbers)
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
        """Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        float_params = ["ssd", "ssad", "offset", "pixel_size_x", "pixel_size_y", "pixel_size_z", "pixel_no_x",
                        "pixel_no_y", "pixel_no_z", "beam_center_x", "beam_center_y", "beam_center_z"]
        set_params(self, params, float_params)

    def calculate_all_beam_centers(self):
        """ Call the functions that calculates the x, y, and z centers

        :return: Nothing as it just doing calculations not outputting them
        :rtype: None
        """
        self.calculate_beam_center_x()
        self.calculate_beam_center_y()
        self.calculate_beam_center_z()

    def calculate_beam_center_x(self):
        """ Calculates the beam center x by calling functions to get the values no_x, size_x and the offset

        :return: Returns nothing but in the end sets the beam center x
        :rtype: None
        """
        # Find the number of x pixels in the detector
        x_pixels = self.pixel_no_x
        # Get pixel size in mm and convert to cm
        dr = self.get_pixel_size_x()
        # Get detector offset in cm
        offset = self.get_offset()
        self.beam_center_x = x_pixels / 2 + 0.5 if dr == 0 else offset / dr + x_pixels / 2 + 0.5

    def calculate_beam_center_y(self):
        """ Calculates the beam center y by calling functions to get the values no_y

        :return: Returns nothing but in the end sets the beam center y
        :rtype: None
        """
        # Find the number of y pixels in the detector
        y_pixels = self.pixel_no_y
        # Get detector offset in cm
        self.beam_center_y = y_pixels / 2 + 0.5

    def calculate_beam_center_z(self):
        """ Calculates the beam center z by calling functions to get the values no_z

        :return: Returns nothing but in the end sets the beam center z
        :rtype: None
        """
        # Find the number of x pixels in the detector
        z_pixels = self.pixel_no_z
        # Get detector offset in cm
        self.beam_center_z = z_pixels / 2 + 0.5

    def get_pixel_size_x(self):
        """Gets the pixel_size_x attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the pixel_size_x
        :rtype: float
        """
        return self.pixel_size_x

    def get_pixel_size_y(self):
        """Gets the pixel_size_y attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the pixel_size_y
        :rtype: float
        """
        return self.parent.d_converter(self.pixel_size_y, self.pixel_size_y_unit)

    def get_pixel_size_z(self):
        """Gets the pixel_size_z attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the pixel_size_z
        :rtype: float
        """
        return self.parent.d_converter(self.pixel_size_z, self.pixel_size_z_unit)

    def get_sdd(self):
        """Gets the sample to detector distance attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the sdd
        :rtype: float
        """
        return self.sdd

    def get_sadd(self):
        """Gets the sample to aperture detector distance attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the sadd
        :rtype: float
        """
        self.sadd = self.sdd + self.aperture_offset
        return self.sadd

    def get_offset(self):
        """Gets the offset attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the offset
        :rtype: float
        """
        return self.offset

    def calculate_distance_from_beam_center(self, coefficient):
        """Calculates the distance from the beams center to the point in question

        :param int coefficient: The integer of the coefficient that is passed into the calculation
        :return: The calculated value of the distance from beam center
        :rtype: float
        """
        pixel_array = np.array(self.pixel_no_x, self.pixel_no_y)
        # FIXME: This should be more than just pixel size in x
        raw_value = pixel_array * self.get_pixel_size_x()
        return coefficient * math.tan((raw_value / coefficient))


class Guide:
    """A class for storing and manipulating Guide related data.

    :param Instrument self.parent: A parent object that has all the objects
    :param float self.guide_width: Thw width of the guides
    :param str self.guide_width_unit: The unit for the width of the guides
    :param float self.transmission_per_guide: The percent of neutrons that pass through each neutron guide.
    :param float self.length_per_guide: The length of each evidential guides
    :param float self.length_per_guide_unit: The unit for the length of each evidential guides
    :param float self.number_of_guides: The number of guides set by the user
    :param boolean self.lenses: A boolean for if there are lenses
    :param float self.gap_at_start: The gap at the start of the guides
    :param float self.gap_at_start_unit: The unit of the gap at the start of the guides
    :param float self.maximum_length: The maximum length for an individual guide
    :param float self.maximum_length_unit: The unit for the maximum length for an individual guide
    """

    def __init__(self, parent, params):
        """Creates object parameters for Detector class and runs set params method Sets object parameters
        self.parent, self.guide_width, self.guide_width_unit, self.transmission_per_guide, self.length_per_guide,
        self.length_per_guide_unit, self.number_of_guides, self.lenses, self.gap_at_start, self.gap_at_start_unit,
        self.maximum_length, and self.maximum_length_unit

        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :return: None as it just sets the parameters
        :rtype: None
        """
        self.parent = parent
        self.guide_width = 0.0
        self.guide_width_unit = 'cm'
        self.transmission_per_guide = 1.0  # GuideLoss
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
        """Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        float_params = ["guide_width", "length_per_guide", "number_of_guides", "gap_at_start", "maximum_length"]
        set_params(self, params, float_params)

    def get_gap_at_start(self):
        """Gets the gap_at_start attribute from the Guide object and converts it for distance with its unit

        :return: The converted value of the gap_at_start
        :rtype: float
        """
        return self.parent.d_converter(self.gap_at_start, self.gap_at_start_unit)

    def get_guide_width(self):
        """Gets the guide_width attribute from the Guide object and converts it for distance with its unit

        :return: The converted value of the guide_width
        :rtype: float
        """
        return self.parent.d_converter(self.guide_width, self.guide_width_unit)

    def get_length_per_guide(self):
        """Gets the length_per_guide attribute from the Guide object and converts it for distance with its unit

        :return: The converted value of the length_per_guide
        :rtype: float
        """
        return self.parent.d_converter(self.length_per_guide, self.length_per_guide_unit)

    def get_maximum_length(self):
        """Gets the maximum_length attribute from the Guide object and converts it for distance with its unit

        :return: The converted value of the maximum_length
        :rtype: float
        """
        return self.parent.d_converter(self.maximum_length, self.maximum_length_unit)


class Wavelength:
    """A class for storing and manipulating Wavelength related data.

    :param  Instrument self.parent: The parent instrument object
    :param float self.wavelength: The wavelength
    :param float self.wavelength_min: The maximum wavelength(Calculated from wavelength_constants)
    :param float self.wavelength_max: The minimum wavelength(Calculated from wavelength_constants)
    :param float self.wavelength_unit: The unit for all the wavelengths(Typically nm)
    :param float self.wavelength_spread: The percent variation in the neutron wavelength.
    :param float self.wavelength_spread_unit: The unit for wavelength spread(Typically %)
    :param tuple self.wavelength_constants: An array of wavelength constants
    :param tuple self.rpm_range: The range of revolutions per minute
    :param float self.number_of_attenuators: The calculated number of attenuators needed for a transmission measurement
    :param float self.attenuation_factor: The minimum attenuation factor required to bring the neutron flux below the
        detector safety threshold.
    :param Converter self.d_converter: A converter with values for wavelength units
    """

    def __init__(self, parent, params):
        """ Creates object parameters for Wavelength class and runs set params method

        Sets object parameters self.parent, self.wavelength, self.wavelength_min, self.wavelength_max,
        self.wavelength_unit, self.wavelength_spread, self.wavelength_spread_unit, self.wavelength_constants,
        self.rpm_range, self.number_of_attenuators, self.attenuation_factor, and self.d_converter

        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :return: None as it just sets the parameters
        :rtype: None
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
        # FOM converter
        self.d_converter = Converter(self.wavelength_unit)
        # TODO Create WavelengthCalculator class and implement object
        # self.d_lambda_allowed = WavelengthCalculator...

        self.set_params(params)

    def set_params(self, params=None):
        """Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        float_params = ["wavelength", "wavelength_min", "wavelength_spread", "number_of_attenuators",
                        "attenuation_factor"]
        set_params(self, params, float_params)
        self.calculate_wavelength_range()

    def get_wavelength(self):
        """Gets the wavelength attribute from the Wavelength object and converts it for distance with its unit

        :return: The converted value of the wavelength
        :rtype: float
        """
        return self.d_converter(self.wavelength, self.wavelength_unit)

    def set_wavelength(self, value, units):
        """ Sets the value of the wavelength to the value parameter and converts it with the units

        :param float value: The value to set it too
        :param str units: The units to be used to convert it
        :return: Nothing as it sets the value and does not return it
        :rtype: None
        """
        self.wavelength = self.d_converter(value, units)

    def calculate_wavelength_range(self):
        """ Calculate the wavelength range based off the wavelength
         Uses wavelength_constants and rpm range if rpm_range[1] is not 0
         If not uses the min/max as 0.0 and infinity respectively

        :return: Nothing as it sets and calculates the values
        :rtype: None
        """
        try:
            calculated_min = self.wavelength_constants[0] + (self.wavelength_constants[1] / self.rpm_range[1])
        except ZeroDivisionError:
            calculated_min = 0.0
        self.wavelength_min = calculated_min if calculated_min > self.wavelength_min else self.wavelength_min
        try:
            calculated_max = self.wavelength_constants[0] + (self.wavelength_constants[1] / self.rpm_range[0])
        except ZeroDivisionError:
            calculated_max = np.inf
        self.wavelength_max = calculated_max if calculated_max < self.wavelength_max else self.wavelength_max


class Data:
    """A class for storing and manipulating Data related data.

    :param  Instrument self.parent: The parent instrument object
    :param float self.beam_diameter: The diameter of the beam that was calculated
    :param str self.beam_diameter_unit: The unit of the diameter of the beam
    :param float self.calculated_beam_stop_diameter: The calculated beam stop diameter value
    :param float self.peak_flux: The maximum beam flux
    :param float self.peak_wavelength: The maximum wavelength
    :param float self.bs_factor: The minimum factor that should be applied to the calculated beam size to ensure the
        beam stop is large enough to fully cover the direct beam
    :param float self.trans_1: Empirical transmission factor of the velocity selector area
    :param float self.trans_2: Empirical transmission factor correction
    :param float self.trans_3: Empirical transmission factor of the sample area
    :param float self.beta: The beta value or B
    :param float self.charlie: The charlie value or c
    :param float self.q_max: The maximum Q value (calculated from slicer)
    :param float self.q_max_horizon: The max horizontal value (calculated from slicer)
    :param float self.q_max_vert: The max vertical value (calculated from slicer)
    :param str self.q_unit: The unit for the q values
    :param float self.q_min: The overall minimum value
    :param list self.q_values: An array of q values
    :param float self.figure_of_merit: The calculated figure of merit value
    :param list self.intensity: The list of values for q intensity
    :param float self.flux: The beam flux values
    :param str  self.flux_size_unit: The size unit for beam flux(Usually cm)
    :param str self.flux_time_unit: The time unit for beam flux (Usually s)
    """

    def __init__(self, parent, params):
        """Creates object parameters for Data class and runs set params method

        Sets object parameters self.parent, self.peak_flux, self.peak_wavelength, self.bs_factor, self.trans_1,
        self.trans_2, self.trans_3, self.beta, self.charlie, self.q_max, self.q_max_horizon, self.q_max_vert,
        self.q_unit, self.q_min, self.q_values, self.intensity, self.flux, self.flux_size_unit, and self.flux_time_unit


        :param Instrument parent: The Instrument instance this Detector is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :return: None as it just sets the parameters
        :rtype: None
        """
        self.parent = parent
        self.beam_diameter = 0.0
        self.beam_diameter_unit = 'cm'
        self.calculated_beam_stop_diameter = 0.0
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
        self.figure_of_merit = 0.0
        self.flux = 0.0
        self.flux_size_unit = 'cm'
        self.flux_time_unit = 's'
        self.set_params(params)

    def set_params(self, params=None):
        """Set class attributes based on a dictionary of values using the generic set_params function.

        :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
        :rtype: None
        """
        set_params(self, params)

    def calculate_beam_flux(self):
        """ Calculate the beam flux range based off lots of different parameter from other classes

        :return: Nothing as it sets and calculates the beam_flux value
        :rtype: None
        """
        # Run calculation methods
        self.parent.calculate_source_to_sample_aperture_distance()
        self.parent.collimation.calculate_source_to_sample_distance()
        self.parent.get_source_to_sample_aperture_distance()
        self.parent.get_source_to_sample_distance()

        # Variable definition
        guide_loss = self.parent.collimation.guides.transmission_per_guide
        source_aperture = self.parent.get_source_aperture_diam()
        sample_aperture = self.parent.get_sample_aperture_diam()
        SSD = self.parent.collimation.get_ssd()
        wave = self.parent.get_wavelength()
        lambda_spread = self.parent.get_wavelength_spread()
        guides = self.parent.get_number_of_guides()

        # Run calculations
        alpha = (source_aperture + sample_aperture) / (2 * SSD)
        f = (self.parent.collimation.guides.get_gap_at_start() * alpha) / (
                2 * self.parent.collimation.guides.get_guide_width())
        trans4 = (1 - f) * (1 - f)
        trans5 = math.exp(guides * math.log(guide_loss))
        trans6 = 1 - (wave * (self.beta - ((guides / 8) * (self.beta - self.charlie))))
        total_trans = self.trans_1 * self.trans_2 * self.trans_3 * trans4 * trans5 * trans6

        area = math.pi * sample_aperture * sample_aperture / 4
        d2_phi = self.peak_flux / (2 * math.pi)
        d2_phi = d2_phi * math.exp(4 * math.log(self.peak_wavelength / wave))
        d2_phi = d2_phi * math.exp(-1 * math.pow(self.peak_wavelength / wave, 2))
        solid_angle = (math.pi / 4) * ((source_aperture / SSD) * (source_aperture / SSD))
        self.flux = area * d2_phi * lambda_spread * solid_angle * total_trans

    def calculate_min_and_max_q(self, index=0):
        """ Calculate the maximum and minimum q range and max horizontal and vertical q values

        :return: Nothing as it calculates and sets the q_max, q_min, q_max_horizon, and q_max_vert
        :rtype: None
        """
        sdd = self.parent.get_sample_to_detector_distance()
        offset = self.parent.get_detector_offset()
        wave = self.parent.get_wavelength()
        pixel_size_x = self.parent.detectors[index].get_pixel_size_x()
        pixel_size_y = self.parent.detectors[index].get_pixel_size_y()
        det_width = pixel_size_x * self.parent.detectors[index].pixel_no_x
        bs_projection = math.fabs(self.parent.calculate_beam_stop_projection())
        # Calculate Q-maximum and populate the page
        radial = math.sqrt(math.pow(0.5 * det_width, 2) + math.pow((0.5 * det_width) + offset, 2))
        pi_over_lambda = math.pi / wave
        four_pi_wave = 4 * pi_over_lambda
        self.q_max = four_pi_wave * math.sin(0.5 * math.atan(radial / sdd))
        # Calculate Q-minimum and populate the page
        self.q_min = pi_over_lambda * (bs_projection + pixel_size_x + pixel_size_y) / sdd  # Working correctly
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) + offset) / sdd)
        self.q_max_horizon = four_pi_wave * math.sin(0.5 * theta)
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) / sdd))
        self.q_max_vert = four_pi_wave * math.sin(0.5 * theta)

    def calculate_figure_of_merit(self):
        """ Calculates the figure of merit from the wavelength and beam flux value

        :return: An integer form of the figure of merit
        :rtype: int
        """
        self.figure_of_merit = math.pow(self.parent.wavelength.get_wavelength(), 2) * self.get_beam_flux()
        return int(self.figure_of_merit)

    def calculate_beam_diameter(self, index=0, direction='maximum'):
        """ Calculates the beam diameter from the ssad and ssd among other values

        + Usually run by calculate_instrument_parameters

        :param index: The index in the detector array
        :param direction: Calculates the beam diameter based on the directory given
        :return: Nothing as it just sets the value
        :rtype: None
        """

        # Get instrumental values
        source_aperture = self.parent.get_source_aperture_diam()  # Correct if diam
        sample_aperture = self.parent.get_sample_aperture_diam()  # Correct if diam
        ssd = self.parent.get_source_to_sample_distance()  # Correct if ssd not SSAD
        sdd = self.parent.get_sample_to_detector_distance(index)  # Correct when sdd not sadd(as SADD DNE)

        wavelength = self.parent.get_wavelength()  # lambda
        wavelength_spread = self.parent.get_wavelength_spread()  # lambda delta

        # Parameters above this point correct

        if self.parent.collimation.guides.lenses:
            # If LENS configuration, the beam size is the source aperture size
            # FIXed: This is showing -58 cm... Why?!?! - it wa snot returning afterward
            self.beam_diameter = source_aperture  # Made beam diameter and returned
            return
        # Calculate beam width on the detector
        try:
            beam_width = source_aperture * sdd / ssd + sample_aperture * (ssd + sdd) / ssd  # Correct calculation
        except ZeroDivisionError:
            beam_width = 0.0
        # Beam height due to gravity
        bv3 = ((ssd + sdd) * sdd) * wavelength ** 2
        bv4 = bv3 * wavelength_spread
        bv = beam_width + 0.0000000125 * bv4  # 0.0000125 != 0.0000000125 Changed to 1.25e-8
        # Larger of the width*safetyFactor and height
        bm_bs = self.bs_factor * beam_width
        bm = bm_bs if bm_bs > bv else bv
        if direction == 'vertical':
            beam_diam = bv
        elif direction == 'horizontal':
            beam_diam = bm_bs
        else:
            beam_diam = bm
        self.beam_diameter = beam_diam

    def calculate_beam_stop_diameter(self, index=0):
        """ Calculates the beam stop diameter

        + Runs calculate beam diameter

        :param int index: The index in the detector array
        :return: Nothing as it just sets the values
        :rtype: None
        """
        self.calculate_beam_diameter(index, 'maximum')
        beam_diam = self.get_beam_diameter()
        for i in self.parent.beam_stops:
            beam_stop_dict = i
            if beam_stop_dict.beam_stop_diameter >= beam_diam:
                self.calculated_beam_stop_diameter = beam_stop_dict.beam_stop_diameter
                return
        else:
            # If this is reached, that means the beam diameter is larger than the largest known beam stop
            self.calculated_beam_stop_diameter = self.parent.beam_stops[
                len(self.parent.beam_stops) - 1].beam_stop_diameter

    def get_figure_of_merit(self):
        """Gets the figure of merit attribute from the Data object and rounds it

        :return: The rounded value of the figure of merit
        :rtype: int
        """
        return int(self.figure_of_merit)

    def get_beam_flux(self):
        """Gets the beam_flux attribute from the Data object and rounds it

        :return: The rounded value of beam_flux
        :rtype: int
        """
        self.flux = round(self.flux)
        # TODO  fix this calculation
        # return (math.pow(self.parent.d_converter(self.flux, self.flux_size_unit), -2)
        #         * math.pow(self.parent.t_converter(self.flux, self.flux_time_unit),-1))
        return self.flux

    def get_beam_diameter(self):
        """ Gets the beam_diameter from the data class

        :return: The value of the beam_diameter
        :rtype: float
        """

        return self.beam_diameter

    def get_calculated_beam_stop_diameter(self):
        """ Gets the calculated_beam_stop_diameter from the data class

        :return: The value of the calculated_beam_stop_diameter
        :rtype: float
        """
        return self.calculated_beam_stop_diameter
