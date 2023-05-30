import json
import math
import numpy as np
from typing import Dict, List, Union

from .units import Converter
from .constants import Constants
from .slicers import Circular
from .slicers import Sector
from .slicers import Rectangular
from .slicers import Elliptical
from .helpers import encode_json


def calculate_instrument(instrument: str, params: dict) -> dict:
    """The base calculation script. Creates an instrument class, calculates the instrumental resolution for the
    configuration, and returns two list of intensities

    :param str instrument: The instrument that we're doing the calculations based off of
    :param dict params: A dictionary of parameters inputted by the user in the JavaScript
    :return: The python return dictionary
    :rtype: dict
    Args:
        instrument: String defining instrument name
        params: Dictionary containing the following information:
            {
                "param_name_001" :
                    {
                        name: str,  # Display name for parameter
                        default: Union[float, int, str],  # Current value
                        type: Optional[str],  # input type, either ["string", "number", or "option"]
                        min: Optional[Union[float, int, str]],
                        max: Optional[Union[float, int, str]],
                        options: Optional[List],
                        unit: Optional[str],
                    },
                ...
            }

    Returns: {
        Qx: [],
        dQx: [],
        Qy: [],
        dQy: [],
        Iqxy: [],
        q: [],
        dq: [],
        Iq: [],
        beamflux: float,

    }
    """
    # i_class is the python object for the interment
    if instrument == 'ng7':
        # Creates NG7SANS object if instrument is ng7
        i_class = NG7SANS(instrument, params)
    elif instrument == 'ngb30':
        # Creates NGB30SANS object if instrument is ngb30
        i_class = NGB30SANS(instrument, params)
    elif instrument == 'ngb10':
        # Creates NG7B10SANS object if instrument is ngb10
        i_class = NGB10SANS(instrument, params)
    else:
        # Create a user-defined Q-range instrument
        i_class = NoInstrument(instrument, params)
    # Runs the SasCalc function and returns the python return array
    return i_class.sas_calc()


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

    def __init__(self, parent, params):
        """Creates object parameters for BeamStop class and runs set params method
        Sets object parameters parent, diameter, diameter_unit, offset, and offset_unit

        :param  Instrument parent: The Collimation instance this Aperture object is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :returns: Nothing as it just sets all the parameters
        :rtype: None
        """
        self.parent = parent
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
    :param float self.diameter:
    :param str self.diameter_unit:
    :param float self.offset: The beam stop offset
    :param str self.offset_unit: The unit for the beam stop offset
    :param float self.beam_stop_size:  The beam stop size
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
        self.parent = parent
        self.diameter = 0.0
        self.diameter_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.beam_stop_size = 0.0
        self.beam_stop_diameter = 0.0
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
        self.source_aperture = Aperture(parent, params.pop('source_aperture', {}))
        self.sample_aperture = Aperture(parent, params.pop('sample_aperture', {}))
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
        self.calculate_source_to_sample_distance()
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
        self.ssad = (self.guides.get_maximum_length() - self.guides.get_length_per_guide()
                     * self.guides.number_of_guides - self.get_sample_aperture_offset())
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
    :param  float self.pixel_no_x:  TODO DOCS figure out the point of this
    :param  float self.pixel_no_y:
    :param  float self.pixel_no_z:
    :param  float self.per_pixel_max_flux:
    :param  float self.dead_time:
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
        self.pixel_no_x = 128
        self.pixel_no_y = 128
        self.pixel_no_z = 128
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
        float_params = ["ssd", "ssad", "offset", "pixel_size_x", "pixel_size_y", "pixel_size_z",
                        "pixel_no_x", "pixel_no_y", "pixel_no_z", "beam_center_x", "beam_center_y", "beam_center_z"]
        set_params(self, params, float_params)

        # Calculate all beam centers using existing values
        self.calculate_all_beam_centers()

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
        return self.parent.d_converter(self.pixel_size_x, self.pixel_size_x_unit)

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
    :param float self.transmission_per_guide: TODO DOCS  - Ask what this is for
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
    :param float self.wavelength_spread: TODO DOCS Ask what this is for
    :param float self.wavelength_spread_unit: The unit for wavelength spread(Typically %)
    :param tuple self.wavelength_constants: An array of wavelength constants
    :param tuple self.rpm_range: The range of revolutions per minute
    :param float self.number_of_attenuators: TODO DOCS Ask what this is for
    :param float self.attenuation_factor: TODO DOCS Ask what this is for
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
            calculated_max = np.Inf
        self.wavelength_max = calculated_max if calculated_max < self.wavelength_max else self.wavelength_max


class Data:
    """A class for storing and manipulating Data related data.

    :param  Instrument self.parent: The parent instrument object
    :param float self.peak_flux: The maximum beam flux
    :param float self.peak_wavelength: The maximum wavelength
    :param float self.bs_factor: TODO docs ask what this is for
    :param float self.trans_1: TODO docs ask what this is for
    :param float self.trans_2: TODO docs ask what this is for
    :param float self.trans_3: TODO docs ask what this is for
    :param float self.beta: The beta value or B
    :param float self.charlie: The charlie value or c
    :param float self.q_max: The maximum Q value (calculated from slicer)
    :param float self.q_max_horizon: The max horizontal value (calculated from slicer)
    :param float self.q_max_vert: The max vertical value (calculated from slicer)
    :param str self.q_unit: The unit for the q values
    :param float self.q_min: The overall minimum value
    :param list self.q_values: An array of q values
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
        # Beam Flux Calculations now correct

        # Variable definition
        guide_loss = self.parent.collimation.guides.transmission_per_guide
        source_aperture = self.parent.get_source_aperture_diam()
        sample_aperture = self.parent.get_sample_aperture_diam()
        self.parent.calculate_source_to_sample_aperture_distance()
        self.parent.collimation.calculate_source_to_sample_distance()
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
        det_width = pixel_size_x * self.parent.detectors[index].pixel_no_x / 100
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

    def get_beam_flux(self):
        """Gets the beam_flux attribute from the Data object and rounds it

        :return: The rounded value of beam_flux
        :rtype: int
        """
        self.calculate_beam_flux()
        # Round up for integer value
        # Question: be sure we want that
        self.flux = round(self.flux)
        # TODO  fix this calculation
        # return (math.pow(self.parent.d_converter(self.flux, self.flux_size_unit), -2)
        #         * math.pow(self.parent.t_converter(self.flux, self.flux_time_unit),-1))
        return self.flux


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
    :param Constant self.constants: A constant object that handles the constant s for the data
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
        self.slicer = None
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.data = None
        self.collimation = None
        self.wavelength = None
        self.detectors = None
        self.beam_stops = None
        self.beam_flux = None
        self.one_dimensional = {"I": None, "dI": None, "Q": None, "dQ": None, "fSubS": None}
        self.two_dimensional = {"I": None, "dI": None, "Qx": None, "dQx": None, "Qy": None, "dQy": None, "fSubS": None}
        if not params:
            params = {}
            # Only store values used for calculations in Instrument class
        self.name = name
        self.constants = Constants()
        self.params = params

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
        name = self.name
        # Instrument class parameters
        self.beam_flux = old_params[name + "BeamFlux"]["default"] if old_params[name + "BeamFlux"][
                                                                         "default"] != "" else None

        # Start 3/14 update the parameters with if statements
        params = {}
        beam_stops = old_params.get(name + "BeamStopSizes", {})
        params["beam_stops"] = beam_stops.get("options", [{'beam_stop_diameter': 1.0, 'beam_diameter': 1.0}])
        params["collimation"] = {}
        params["collimation"]["guides"] = {}
        params["collimation"]["guides"]["lenses"] = self.guide_lens_config(old_params[name + "GuideConfig"]["default"],
                                                                           False) if \
            old_params[name + "GuideConfig"]["default"] != "" else None
        params["collimation"]["guides"]["number_of_guides"] = self.guide_lens_config(
            old_params[name + "GuideConfig"]["default"],
            True) if old_params[name + "GuideConfig"][
                         "default"] != "" else None
        params["collimation"]["sample_aperture"] = {}
        params["collimation"]["sample_aperture"]["diameter"] = old_params[name + "SampleAperture"]["default"] * 2.54 if \
            old_params[name + "SampleAperture"]["default"] != "" else None
        params["collimation"]["source_aperture"] = {}
        params["collimation"]["source_aperture"]["diameter_unit"] = old_params[name + "SourceAperture"]["unit"] if \
            old_params[name + "SourceAperture"]["unit"] != "" else None
        params["collimation"]["source_aperture"]["diameter"] = old_params[name + "SourceAperture"]["default"] if \
            old_params[name + "SourceAperture"]["default"] != "" else None
        params["collimation"]["detector_distance"] = old_params[name + "SDDInputBox"]["default"] if \
            old_params[name + "SDDInputBox"]["default"] != "" else None
        if name + "SampleTable" in old_params.values():
            params["collimation"]["sample_space"] = old_params[name + "SampleTable"]["default"] if \
                old_params[name + "SampleTable"][
                    "default"] != "" else None
        params["collimation"]["ssad_unit"] = old_params[name + "SSD"]["unit"] if old_params[name + "SSD"][
                                                                                          "unit"] != "" else None
        params["collimation"]["ssad"] = old_params[name + "SSD"]["default"] if old_params[name + "SSD"][
                                                                                        "default"] != "" else None
        params["collimation"]["ssd_unit"] = old_params[name + "SSD"]["unit"] if old_params[name + "SSD"][
                                                                                         "unit"] != "" else None
        params["collimation"]["ssd"] = old_params[name + "SSD"]["default"] if old_params[name + "SSD"][
                                                                                       "default"] != "" else None
        params["detectors"] = [None]
        params["detectors"][0] = {}
        offset_params = old_params.get(name + "OffsetInputBox", {})
        if any(offset_params):
            params["detectors"][0]["offset_unit"] = old_params[name + "OffsetInputBox"]["unit"] if \
                old_params[name + "OffsetInputBox"]["unit"] != "" else None
            params["detectors"][0]["offset"] = old_params[name + "OffsetInputBox"]["default"] if \
                old_params[name + "OffsetInputBox"]["default"] != "" else None
        params["detectors"][0]["sdd_unit"] = old_params[name + "SDDInputBox"]["unit"] if old_params[name + "SDDInputBox"][
                                                                                     "unit"] != "" else None
        params["detectors"][0]["sdd"] = old_params[name + "SDDInputBox"]["default"] if old_params[name + "SDDInputBox"][
                                                                                   "default"] != "" else None
        params["slicer"] = {}
        # params["slicer"]["averaging_params"] =
        params["average_type"] = calculate_params["slicer"]
        params["wavelength"] = {}
        params["wavelength"]["attenuation_factor"] = old_params[name + "AttenuationFactor"]["default"] if \
            old_params[name + "AttenuationFactor"]["default"] != "" else None
        params["wavelength"]["number_of_attenuators"] = old_params[name + "CustomAperture"]["default"] if \
            old_params[name + "CustomAperture"]["default"] != "" else None
        params["wavelength"]["wavelength_spread_unit"] = old_params[name + "WavelengthSpread"]["unit"] if \
            old_params[name + "WavelengthSpread"]["unit"] != "" else None
        params["wavelength"]["wavelength_spread"] = old_params[name + "WavelengthSpread"]["default"] / 100 if \
            old_params[name + "WavelengthSpread"]["default"] != "" else None
        params["wavelength"]["wavelength_unit"] = old_params[name + "WavelengthInput"]["unit"] if \
            old_params[name + "WavelengthInput"][
                "unit"] != "" else None
        params["wavelength"]["wavelength"] = old_params[name + "WavelengthInput"]["default"] if \
            old_params[name + "WavelengthInput"][
                "default"] != "" else None
        return params

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

        Runs calculate_sample_to_detector_distance and calculate_min_and_max_q.
        Create objects beam_stops, detectors, collimation, and wavelength

        :param dict params: A dictionary of parameters to send to the initialization of the objects
        :return: Nothing as it just sets up all the objects
        :rtype: None
        """
        # Creates the objects with the param array
        #       (This is not a part of load params so instrument can have default values if necessary)

        # CAF Beam stop defined
        self.beam_stops = params.get('beam_stops', [{'beam_stop_diameter': 1.0, 'beam_diameter': 1.0}])
        self.detectors = [Detector(self, detector_params) for detector_params in params.get('detectors', [{}])]
        self.collimation = Collimation(self, params.get('collimation', {}))
        self.wavelength = Wavelength(self, params.get('wavelength', {}))
        # TODO   What class should be imported into data
        self.data = Data(self, params.get('data', {}))

        # gets the parameters for slicer object and updates the parameters dictionary for that

        # Creates slicer param objects
        self.averaging_type = params.get("average_type", "ERROR")
        self.slicer_params = params.get('slicer', {})

        self.calculate_sample_to_detector_distance()
        self.data.calculate_min_and_max_q()

    def sas_calc(self):
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
        python_return["user_inaccessible"] = {}
        python_return["user_inaccessible"]["BeamFlux"] = self.data.get_beam_flux()
        python_return["user_inaccessible"]["FigureOfMerit"] = self.calculate_figure_of_merit()
        python_return["user_inaccessible"]["Attenuators"] = self.get_attenuator_number()
        python_return["user_inaccessible"]["SSD"] = self.collimation.ssd
        python_return["user_inaccessible"]["SDD"] = self.detectors[0].get_sdd()
        python_return["user_inaccessible"]["BeamDiameter"] = int(self.get_beam_diameter() * 10000) / 10000
        python_return["user_inaccessible"]["BeamStopSize"] = self.get_beam_stop_diameter()
        python_return["user_inaccessible"]["AttenuationFactor"] = self.get_attenuation_factor()
        python_return["user_inaccessible"]["MaximumVerticalQ"] = self.data.q_max_vert
        python_return["user_inaccessible"]["MaximumHorizontalQ"] = self.data.q_max_horizon
        python_return["user_inaccessible"]["MaximumQ"] = self.data.q_max
        python_return["user_inaccessible"]["MinimumQ"] = self.data.q_min
        python_return["nCells"] = self.slicer.n_cells.tolist()
        python_return["qsq"] = self.slicer.d_sq.tolist()
        python_return["sigmaAve"] = self.slicer.sigma_ave.tolist()
        python_return["qAverage"] = self.slicer.q_average.tolist()
        python_return["sigmaQ"] = self.slicer.sigma_q.tolist()
        python_return["fSubs"] = self.slicer.f_subs.tolist()
        python_return["qxValues"] = self.slicer.qx_values.tolist()
        python_return["qyValues"] = self.slicer.qy_values.tolist()
        python_return["q2DValues"] = self.slicer.q_2d_values.tolist()
        python_return["intensity2D"] = self.slicer.intensity_2D.tolist()
        python_return["qValues"] = self.slicer.q_values.tolist()
        python_return["slicer_params"] = self.slicer.slicer_return()
        # Can return encode JSON just not a python dictionary
        return encode_json(python_return)

    def calculate_instrument_parameters(self):
        """Uses the many functions to calculate all the necessary parameters necessary for an instrument

        * This function is usually called by the sas calc function
        * Calculates beam stop diameter, beam flux, figure of merit, attenuator number, slicer array values, sdd, and min and max q values

        :return: It returns nothing as each function sets the value it calculates
        :rtype: None
        """
        # Calculate the beam stop diameter
        self.calculate_beam_stop_diameter()
        # Calculate the estimated beam flux
        self.data.calculate_beam_flux()
        # Calculate the figure of merit
        self.calculate_figure_of_merit()
        # Calculate the number of attenuators
        self.calculate_attenuator_number()
        self.calculate_slicer()
        self.calculate_sample_to_detector_distance()
        self.data.calculate_min_and_max_q()

    def calculate_attenuation_factor(self, index=0):
        """Calculates the attenuation factors from te sample aperture diameter and returns the calculated value

        * Usually run by the calculate attenuator number function

        :param index: The index of the value to fin in the detectors array
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

    def calculate_beam_diameter(self, index=0, direction='maximum'):
        """ Calculates the beam diameter from the ssad and ssd among other values

        + Usually run by calculate_instrument_parameters

        :param index: The index in the detector array
        :param direction: Calculates the beam diameter based on the directory given
        :return: Nothing as it just sets the value
        :rtype: None
        """
        # CAF Needs function to be fixed

        # Update all instrument calculations needed for beam diameter
        self.collimation.get_ssad()
        self.get_sample_to_detector_distance(index)

        # Get instrumental values
        source_aperture = self.get_source_aperture_diam()  # Correct if diam
        sample_aperture = self.get_sample_aperture_diam()  # Correct if diam
        ssd = self.get_source_to_sample_distance()  # Correct if ssd not SSAD
        sdd = self.get_sample_to_detector_distance(index)  # Correct when sdd not sadd(as SADD DNE)
        wavelength = self.get_wavelength()  # lambda
        wavelength_spread = self.get_wavelength_spread()  # lambda delta

        # Parameters above this point correct

        if self.collimation.guides.lenses:
            # If LENS configuration, the beam size is the source aperture size
            # FIXed: This is showing -58 cm... Why?!?! - it wa snot returning afterward
            self.beam_stops[index]["beam_diameter"] = source_aperture  # Made beam diameter and returned
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
        """ Calculates the beam stop diameter

        + Runs calculate beam diameter

        :param int index: The index in the detector array
        :return: Nothing as it just sets the values
        :rtype: None
        """
        self.calculate_beam_diameter(index, 'maximum')
        beam_diam = self.get_beam_diameter(index)
        for i in self.beam_stops:
            beam_stop_dict = i
            if beam_stop_dict.get("beam_stop_diameter") >= beam_diam:
                self.beam_stops[index]["beam_stop_diameter"] = beam_stop_dict["beam_stop_diameter"]
                return
        else:
            # If this is reached, that means the beam diameter is larger than the largest known beam stop
            self.beam_stops[index]['beam_stop_diameter'] = self.beam_stops[len(self.beam_stops) - 1][
                'beam_stop_diameter']

    def calculate_beam_stop_projection(self, index=0):
        """ Calculates the projection of the beam stop TODO DOCS add more here

        :param int index: The index in the detector array
        :return: The calculated projection
        :rtype: Float
        """
        self.get_sample_to_detector_distance(index)
        self.calculate_beam_diameter(index)
        self.calculate_beam_stop_diameter(index)
        bs_diam = self.get_beam_stop_diameter(index)
        sample_aperture = self.get_sample_aperture_size()
        l2 = self.get_sample_aperture_to_detector_distance()  # Question why do we no longer need aperture offset
        l_beam_stop = 20.1 + 1.61 * bs_diam  # distance in cm from beam stop to anode plane (empirical calculation)
        return bs_diam + (bs_diam + sample_aperture) * l_beam_stop / (l2 - l_beam_stop)  # Return in cm

    def calculate_figure_of_merit(self):
        """ Calculates the figure of merit from the wavelength and beam flux value

        :return: An integer form of the figure of merit
        :rtype: int
        """
        figure_of_merit = math.pow(self.get_wavelength(), 2) * self.get_beam_flux()
        return int(figure_of_merit)

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
        return detector.get_sdd()

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
        slicer_params = self.slicer_params

        # QUESTION      [0] Do I need to run a loop here? how does this work with multiple detectors
        self.detectors[index].calculate_beam_center_x()
        self.detectors[index].calculate_beam_center_y()
        slicer_params["x_center"] = self.detectors[index].beam_center_x
        slicer_params["y_center"] = self.detectors[index].beam_center_y
        slicer_params["pixel_size"] = self.detectors[index].pixel_size_x
        slicer_params["lambda_val"] = self.wavelength.get_wavelength()
        slicer_params["detector_distance"] = self.collimation.detector_distance

        slicer_params["lambda_width"] = self.wavelength.wavelength_spread
        slicer_params["guides"] = self.collimation.guides.number_of_guides
        slicer_params["lens"] = self.collimation.guides.lenses
        # QUESTION      Is it get_source_aperture_size or get_source_aperture the javascript defines sourceAperture
        # and sampleAperture differently
        slicer_params["source_aperture"] = self.get_source_aperture_size()
        slicer_params["sample_aperture"] = self.get_sample_aperture_size()
        slicer_params["beam_stop_size"] = self.get_beam_stop_diameter() * 2.54
        slicer_params["SSD"] = self.calculate_source_to_sample_aperture_distance()
        slicer_params["SDD"] = self.calculate_sample_to_detector_distance()
        averaging_type = self.averaging_type
        if averaging_type == "sector":
            self.slicer = Sector(slicer_params)
        elif averaging_type == "rectangular":
            self.slicer = Rectangular(slicer_params)
        elif averaging_type == "elliptical":
            self.slicer = Elliptical(slicer_params)
        else:
            self.slicer = Circular(slicer_params)

    # TODO Fix these run functions and should just be getting values
    def get_attenuation_factor(self):
        """ Gets the attenuation factor

        :return: The result of calculate attenuation factor
        :rtype: Float
        """
        # TODO Fix The attenuation factor value calculated based on the number of attenuators
        return self.calculate_attenuation_factor()

    def get_attenuator_number(self):
        """Runs the calculation for attenuator number

        :return: The result of the calculate attenuator number
        :rtype: Int
        """

        # Number of attenuators in the beam
        return self.calculate_attenuator_number()

    def get_beam_flux(self):
        """ Gets the beam flux value from the data class

        :return: Returns the value of the
        :rtype: int
        """
        # Beam flux in cm^-2-s^-1
        return self.data.get_beam_flux()

    def get_beam_diameter(self, index=0):
        """ Gets the beam diameter value from the bea stops class at the specified index

        :param index: The index in the beam stops array
        :return: Returns the value of the beam diameter
        :rtype: int
        """
        # Beam diameter in centimeters
        return self.beam_stops[index].get("beam_diameter")

    def get_beam_stop_diameter(self, index=0):
        """ Gets the beam stop diameter value from the beam stops class at the specified index

        :param index: The index in the beam stops array
        :return: Returns the value of the beam stop diameter
        :rtype: int
        """
        # Beam stop diameter in inches
        # TODO: Convert to centimeters
        return self.beam_stops[index]["beam_stop_diameter"]

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


class NoInstrument(Instrument):
    """A class for storing and manipulating The No Instrument related data.

    :param int self.n_pts: The number of points from the points dictionary class
    :param str self.spacing:
    :param float self.q_min:
    :param float self.dq:
    :param float self.q_max:
    :param float self._q_max_horizon:
    :param float self._q_max_vert:
    :param float self._q_min_horizon:
    :param float self._q_min_vert:
    :param  self.params:
    """
    # Constructor for the pseudo instrument with user-defined Q ranges and instrument resolutions
    def __init__(self, name, params):
        """

        :param name:
        :param params:
        """
        self.name = name if name else "Q Range"
        super().__init__(name, params)
        self.n_pts = 0
        self.spacing = 'lin'
        self.q_min = 0.0
        self.dq = 0.0
        self.q_max = 0.0
        self._q_max_horizon = 6.0
        self._q_max_vert = 6.0
        self._q_min_horizon = -6.0
        self._q_min_vert = -6.0
        self.params = params
        self.calculate_instrument_parameters()

    @property
    def q_max_vert(self):
        return self._q_max_vert

    @q_max_vert.setter
    def q_max_vert(self, val: float):
        self._q_max_vert = val
        self.set_q_max()

    @property
    def q_min_vert(self):
        return self._q_min_vert

    @q_min_vert.setter
    def q_min_vert(self, val: float):
        self._q_min_vert = val
        self.set_q_max()

    @property
    def q_max_horizon(self):
        return self._q_max_horizon

    @q_max_horizon.setter
    def q_max_horizon(self, val: float):
        self._q_max_horizon = val
        self.set_q_max()

    @property
    def q_min_horizon(self):
        return self._q_min_horizon

    @q_min_horizon.setter
    def q_min_horizon(self, val: float):
        self._q_min_horizon = val
        self.set_q_max()

    def set_q_max(self):
        corners = [
            math.sqrt(self.q_max_vert ** 2 + self.q_max_horizon ** 2),
            math.sqrt(self.q_min_vert ** 2 + self.q_max_horizon ** 2),
            math.sqrt(self.q_max_vert ** 2 + self.q_min_horizon ** 2),
            math.sqrt(self.q_min_vert ** 2 + self.q_min_horizon ** 2),
        ]
        self.q_max = max(corners)

    def load_params(self, params: Dict[str, Dict[str, Union[float, int, str]]]):
        values = {}
        # Simplify the parameters passed into a key:value pairing instead of a key: {sub_key: value} pairing
        for name, value in params.items():
            def_value = 0.0 if value.get("type", "number") == "number" else "lin"
            values[name] = value.get("default", def_value)
        self.n_pts = values.get('points', 0.0)
        self.spacing = values.get('point_spacing', self.spacing)
        self.q_min = values.get('q_min', self.q_min)
        self.dq = values.get('dq', self.dq)
        self.q_max_vert = values.get('q_max_vertical', self.q_max_vert)
        self.q_min_vert = values.get('q_min_vertical', self.q_min_vert)
        self.q_max_horizon = values.get('q_max_horizontal', self.q_max_horizon)
        self.q_min_horizon = values.get('q_min_horizontal', self.q_min_horizon)

    def sas_calc(self):
        method = np.linspace if self.spacing == "lin" else np.logspace
        q_vals = method(self.q_min, self.q_max, self.n_pts)
        qx_values = method(self.q_min_horizon, self.q_max_horizon, self.n_pts)
        qy_values = method(self.q_min_vert, self.q_max_vert, self.n_pts)
        q_2d_vals = np.sqrt(qx_values * qx_values + qy_values * qy_values)
        np.broadcast_to(qx_values, (self.n_pts, len(qx_values)))
        np.broadcast_to(qy_values, (self.n_pts, len(qy_values)))
        dq_vals = q_vals * self.dq
        dqx_vals = qx_values * self.dq
        dqy_vals = qy_values * self.dq
        i_vals = np.ones_like(self.n_pts)
        # FIXME: Set points where q_2d_vals < self.q_min to 0
        i_2d_vals = np.ones_like((self.n_pts, self.n_pts))
        # TODO: Populate this
        self.one_dimensional = {"I": None, "dI": None, "Q": None, "dQ": None, "fSubS": None}
        self.two_dimensional = {"I": None, "dI": None, "Qx": None, "dQx": None, "Qy": None, "dQy": None, "fSubS": None}
        return json.dumps(self.params)


class NG7SANS(Instrument):
    """ A class to manipulate NG7SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
    """

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = "ng7"
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
        params["detectors"][0]["pixel_size_y"] = 5.08
        params["detectors"][0]["pixel_size_x_unit"] = "mm"
        params["detectors"][0]["pixel_size_y_unit"] = "mm"
        params["detectors"][0]["pixel_no_x"] = 128
        params["detectors"][0]["pixel_no_y"] = 128
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


class NGB30SANS(Instrument):
    """ A class to manipulate NGB10SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
    """
    # Class for the NGB 30m SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = "ngb30"
        params = self.param_restructure(params)
        super().__init__(name, params)

    def load_params(self, params):
        """A method that loads the constants of the NG7SANS Instrument

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
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
        params["detectors"][0]["pixel_size_y"] = 5.08
        params["detectors"][0]["pixel_size_x_unit"] = "mm"
        params["detectors"][0]["pixel_size_y_unit"] = "mm"
        params["detectors"][0]["pixel_no_x"] = 128
        params["detectors"][0]["pixel_no_y"] = 128
        params["collimation"]["guides"]["gap_at_start"] = 100
        params["collimation"]["guides"]["guide_width"] = 6.0
        params["collimation"]["guides"]["transmission_per_guide"] = 0.924
        params["collimation"]["aperture_offset"] = 5
        params["slicer"]["coeff"] = 10000
        params["slicer"]["x_pixels"] = 128
        params["slicer"]["y_pixels"] = 128
        params["collimation"]["guides"]["maximum_length"] = 1632
        params["collimation"]["guides"]["length_per_guide"] = 155
        if params.get("collimation").get("sample_space", "Huber") == "Huber":
            params["collimation"]["space_offset"] = 54.8  # HuberOffset
        else:
            params["collimation"]["space_offset"] = 0  # ChamberOffset

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "ngb30sans.ncnr.nist.gov"

        super().load_objects(params)


class NGB10SANS(Instrument):
    """ A class to manipulate NGB10SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
    """
    # Class for the NGB 10m SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = "ngb10"
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
        params["detectors"][0]["pixel_size_x"] = 5.08
        params["detectors"][0]["pixel_size_y"] = 5.08
        params["detectors"][0]["pixel_size_x_unit"] = "mm"
        params["detectors"][0]["pixel_size_y_unit"] = "mm"
        params["detectors"][0]["pixel_no_x"] = 128
        params["detectors"][0]["pixel_no_y"] = 128
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

    # class VSANS(Instrument):
# TODO Implement VSANS
#     # Class for the VSANS instrument
#     def __init__(self, name, params):
#         super().__init__(name, params)
#
#     def load_params(self, params):
#         print("VSANS Load Params")
#         super().load_objects(params)
