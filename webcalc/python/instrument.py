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


# TODO: Replace all nodes with Instrument parameters
# TODO: Call slicer directly using known parameters

# TODO Doc      Add args to top if instrument package html

def calculate_instrument(instrument: str, params: dict) -> dict:
    """ The base calculation script. Creates an instrument class, calculates the instrumental resolution for the
    configuration, and returns two list of intensities

    :param str instrument: The instrument that we're doing the calculations based off of
    :param dict params: A dictionary of parameters inputted by the user in the JavaScript
    :return: The python return dictionary
    :rtype: dict
    # TODO: JRK Note - This is what is currently being passed and will need to be parsed properly.
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
    # TODO: Create classes for all instruments
    print(params)
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


def set_params(instance, params):
    """ Set class attributes based on a dictionary of values. The dict should map <param_name> -> <value>.

    :param instance: An instance of any class type in this file that needs params set in bulk.
    :param dict params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
    :return: Nothing justs prints errors if there are anu
    :rtype: None
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
        set_params(self, params)

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
        set_params(self, params)


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
        set_params(self, params)

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
        set_params(self, params)

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
        return self.parent.d_converter(self.sdd, self.sdd_unit)

    def get_sadd(self):
        """Gets the sample to aperture detector distance attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the sadd
        :rtype: float
        """
        return self.parent.d_converter(self.sadd, self.sadd_unit)

    def get_offset(self):
        """Gets the offset attribute from the Detector object and converts it for distance with its unit

        :return:The converted value of the offset
        :rtype: float
        """
        return self.parent.d_converter(self.offset, self.offset_unit)

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
        set_params(self, params)

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
        set_params(self, params)
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
    """A class for storing and manipulating Wavelength related data.

    :param  Instrument self.parent: The parent instrument object
    :param float self.peak_flux: The maximum beam flux
    :param float self.peak_wavelength: The maximum wavelength
    :param float self.bs_factor: TODO docs ask what this is for
    :param float self.trans_1: TODO docs ask what this is for
    :param float self.trans_2: TODO docs ask what this is for
    :param float self.trans_3: TODO docs ask what this is for
    :param float self.beta: The beta value or B
    :param float self.charlie: The charlie valye or c
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
        """Creates object parameters for Wavelength class and runs set params method

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

        # Varible defintion
        guide_loss = self.parent.collimation.guides.transmission_per_guide
        sourse_aperture = self.parent.get_source_aperture_diam()
        sample_aperture = self.parent.get_sample_aperture_diam()
        self.parent.calculate_source_to_sample_aperture_distance()
        self.parent.collimation.calculate_source_to_sample_distance()
        SSD = self.parent.collimation.get_ssd()
        wave = self.parent.get_wavelength()
        lambda_spread = self.parent.get_wavelength_spread()
        guides = self.parent.get_number_of_guides()

        # Run calculations
        alpha = (sourse_aperture + sample_aperture) / (2 * SSD)
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
        solid_angle = (math.pi / 4) * ((sourse_aperture / SSD) * (sourse_aperture / SSD))
        self.flux = area * d2_phi * lambda_spread * solid_angle * total_trans

    def calculate_min_and_max_q(self, index=0):
        """ Calculate the maximum and minimum q range and max horizontal and vertical q values

        :return: Nothing as it calculates and sets the q_max, q_min, q_max_horizon, and q_max_vert
        :rtype: None
        """
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
        self.q_min = (math.pi / wave) * (bs_projection + pixel_size + pixel_size) / sdd  # Working correctly
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) + offset) / sdd)
        self.q_max_horizon = 4 * (math.pi / wave) * math.sin(0.5 * theta)
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) / sdd))
        self.q_max_vert = 4 * (math.pi / wave) * math.sin(0.5 * theta)

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
    isReal = False

    def __init__(self, name="", params=None):
        # Unit converters
        self.slicer = None
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.data = None
        self.beam_flux = None
        self.one_dimensional = {"I": None, "dI": None, "Q": None, "dQ": None, "fSubS": None}
        self.two_dimensional = {"I": None, "dI": None, "Qx": None, "dQx": None, "Qy": None, "dQy": None, "fSubS": None}
        if not params:
            params = {}
            # Only store values used for calculations in Instrument class
        self.name = name
        self.constants = Constants()
        self._params = params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self.load_params(params)

    def load_params(self, params):
        """Pseudo-abstract method to initialize constants associated with an instrument"""
        raise NotImplementedError(f"Instrument {self.name} has not implemented the `load_params` method.")

    def load_objects(self, params):
        # Creates the objects with the param array
        #       (This is not a part of load params so instrument can have default values if necessary)

        # CAF Beam stop defined
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
        # self.slicer.calculate_q_range_slicer()
        self.calculate_sample_to_detector_distance()
        self.data.calculate_min_and_max_q()

    def sas_calc(self):
        # MainFunction for this class

        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculate_instrument_parameters()

        # Final output returned to the JS
        # FIXME: What values need to be returned?
        # TODO Return Values
        python_return = {}
        python_return["user_inaccessible"] = {}
        python_return["user_inaccessible"]["beamFlux"] = self.data.get_beam_flux()
        python_return["user_inaccessible"]["figureOfMerit"] = self.calculate_figure_of_merit()
        python_return["user_inaccessible"]["numberOfAttenuators"] = self.get_attenuator_number()
        python_return["user_inaccessible"]["ssd"] = self.collimation.ssd
        python_return["user_inaccessible"]["sdd"] = self.detectors[0].sdd
        python_return["user_inaccessible"]["beamDiameter"] = int(self.get_beam_diameter() * 10000) / 10000
        python_return["user_inaccessible"]["beamStopDiameter"] = self.get_beam_stop_diameter()
        python_return["user_inaccessible"]["attenuationFactor"] = self.get_attenuation_factor()
        python_return["MaximumVerticalQ"] = self.data.q_max_vert
        python_return["MaximumHorizontalQ"] = self.data.q_max_horizon
        python_return["MaximumQ"] = self.data.q_max
        python_return["MinimumQ"] = self.data.q_min
        python_return["nCells"] = self.slicer.n_cells.tolist()
        python_return["qsq"] = self.slicer.d_sq.tolist()
        python_return["sigmaAve"] = self.slicer.sigma_ave.tolist()
        python_return["qAverage"] = self.slicer.q_average.tolist()
        python_return["sigmaQ"] = self.slicer.sigma_q.tolist()
        python_return["fSubs"] = self.slicer.f_subs.tolist()
        python_return["qxValues"] = self.slicer.qx_values.tolist()
        python_return["qyValues"] = self.slicer.qy_values.tolist()
        python_return["intensitys2D"] = self.slicer.intensity_2D.tolist()
        python_return["qValues"] = self.slicer.q_values.tolist()
        python_return["slicer_params"] = self.slicer.slicer_return()

        # Can return encode JSON just not a python dictionary
        return encode_json(python_return)

    def calculate_instrument_parameters(self):
        # Calculate the beam stop diameter
        self.calculate_beam_stop_diameter()
        # Calculate the estimated beam flux
        self.data.calculate_beam_flux()
        # Calculate the figure of merit
        self.calculate_figure_of_merit()
        # Calculate the number of attenuators
        self.calculate_attenuator_number()
        # Do Circular Average of an array of 1s

        # TODO Figure out point of this
        # for index in range(len(self.detectors) - 1):
        #     self.data.calculate_min_and_max_q(index)
        #     # TODO: This might not be needed here...
        #     self.slicer.calculate_q_range_slicer(index)

    # Start 1/20/23 fix this function
    def calculate_attenuation_factor(self, index=0):
        a2 = self.get_sample_aperture_diam()  # Correct with diameter instead of radius
        beam_diam = self.get_beam_diameter(index)
        a_pixel = self.detectors[index].get_pixel_size_x() / 100  # Fix: This calc was 100 to high
        i_pixel_max = self.detectors[index].per_pixel_max_flux  # Calculated correctly
        num_pixels = (math.pi / 4) * (0.5 * (a2 + beam_diam) / a_pixel) ** 2
        i_pixel = self.get_beam_flux() / num_pixels
        atten = 1.0 if i_pixel < i_pixel_max else i_pixel_max / i_pixel
        self.wavelength.attenuation_factor = atten if atten == 1.0 else round(atten * 100000) / 100000
        return self.wavelength.attenuation_factor

    def calculate_attenuator_number(self):
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
        self.get_sample_to_detector_distance(index)
        self.calculate_beam_diameter(index)
        self.calculate_beam_stop_diameter(index)
        bs_diam = self.get_beam_stop_diameter(index)
        sample_aperture = self.get_sample_aperture_size()
        l2 = self.get_sample_aperture_to_detector_distance()  # Question why do we no longer need aperture offset
        l_beam_stop = 20.1 + 1.61 * self.get_beam_stop_diameter()  # distance in cm from beam stop to anode plane
        return bs_diam + (bs_diam + sample_aperture) * l_beam_stop / (l2 - l_beam_stop)  # Return in cm

    def calculate_figure_of_merit(self):
        # FOM This would work if beam flux is right
        # TODO replace when beam flux works
        figure_of_merit = math.pow(self.get_wavelength(), 2) * self.get_beam_flux()
        return int(figure_of_merit)

    def calculate_sample_to_detector_distance(self, index=0):
        try:
            detector = self.detectors[index]
        except IndexError:
            detector = self.detectors[0]
        detector.sdd = self.collimation.detector_distance + self.collimation.space_offset
        return detector.get_sdd()

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
        slicer_params["source_aperture"] = self.get_source_aperture_size() * 0.5
        slicer_params["sample_aperture"] = self.get_sample_aperture_size() * 0.5
        slicer_params["beam_stop_size"] = self.get_beam_stop_diameter() * 2.54
        slicer_params["SSD"] = self.calculate_source_to_sample_aperture_distance()
        slicer_params["SDD"] = self.calculate_sample_to_detector_distance()
        del slicer_params["averaging_params"]
        return slicer_params

    def get_attenuation_factor(self):
        # TODO Fix The attenuation factor value calculated based on the number of attenuators
        return self.calculate_attenuation_factor()

    def get_attenuator_number(self):
        # Number of attenuators in the beam
        return self.calculate_attenuator_number()

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

    def get_sample_aperture_diam(self):
        # Sample Aperture diameter in centimeters
        return self.collimation.get_sample_aperture_diameter()

    def get_source_aperture_diam(self):
        # Source Aperture diameter in centimeters
        return self.collimation.get_source_aperture_diameter()

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
        return detector.get_sdd()

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

    def calculate_source_to_sample_aperture_distance(self):
        return self.collimation.calculate_source_to_sample_aperture_distance()


class NoInstrument(Instrument):
    # Constructor for the pseudo instrument with user-defined Q ranges and instrument resolutions
    def __init__(self, name, params):
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
            math.sqrt(self.q_max_vert**2 + self.q_max_horizon**2),
            math.sqrt(self.q_min_vert**2 + self.q_max_horizon**2),
            math.sqrt(self.q_max_vert**2 + self.q_min_horizon**2),
            math.sqrt(self.q_min_vert**2 + self.q_min_horizon**2),
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
        q_2d_vals = np.sqrt(qx_values*qx_values + qy_values*qy_values)
        np.broadcast_to(qx_values, (self.n_pts, len(qx_values)))
        np.broadcast_to(qy_values, (self.n_pts, len(qy_values)))
        dq_vals = q_vals*self.dq
        dqx_vals = qx_values*self.dq
        dqy_vals = qy_values*self.dq
        i_vals = np.ones_like(self.n_pts)
        # FIXME: Set points where q_2d_vals < self.q_min to 0
        i_2d_vals = np.ones_like((self.n_pts, self.n_pts))
        # TODO: Populate this
        self.one_dimensional = {"I": None, "dI": None, "Q": None, "dQ": None, "fSubS": None}
        self.two_dimensional = {"I": None, "dI": None, "Qx": None, "dQx": None, "Qy": None, "dQy": None, "fSubS": None}
        return json.dumps(self.params)


class NG7SANS(Instrument):

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        self.name = "ng7"
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
        params["collimation"]["0"]["aperture_offset"] = 5
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


class NGB30SANS(Instrument):
    # Class for the NGB 30m SANS instrument
    def __init__(self, name, params):
        self.name = "ngb30"
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
        params["collimation"]["0"]["aperture_offset"] = 5
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


class NGB10SANS(Instrument):
    # Class for the NGB 10m SANS instrument
    def __init__(self, name, params):
        self.name = "ngb10"
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
        params["collimation"]["guides"]["maximum_length"] = 513
        if params["collimation"]["guides"]["number_of_guides"] != 0:
            params["collimation"]["guides"]["length_per_guide"] = 150 + (
                    61.9 / params["collimation"]["guides"]["number_of_guides"])
        params["collimation"]["0"]["aperture_offset"] = 5
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

    def calculate_source_to_sample_aperture_distance(self):
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
