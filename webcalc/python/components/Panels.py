import math

import numpy as np

from .DQCalculator import DqCalculator
from ..instrument import Detector as BaseDetector
from ..instrument import set_params
from ..instruments.InstrumentBase import Instrument


class AllCarriage:
    """A class for storing and manipulating AllCarriage related data.

    :param VSANS self.parent: The parent VSANS object
    :param str self.name: The name of the class
    :param float self.imported_l_1:
    :param float self.beam_drop: The beam drop or beam gravity drop mean
    :param float self.gravity_drop_min: The max value of beam gravity drop
    :param float self.gravity_drop_max: The min value of the beam gravity drop
    :param float self.beamstop_required: Calculates the beamstop required value in CM
    :param float self.beamstop: The beam stop value in inches
    :param float self.beam_stop_cm: The beamstop value in cm
    :param float self.two_theta_min: The min value of 2 theta
    :param Boolean self.overall_dq_calculated: Whether the overall dq values had finished calculating yet
    :param float self.dq_geometric: The dq geometric value
    :param float self.dq_wavelength: The dq wavelength value
    :param float self.dq_gravity: The dq gravity value
    """

    def __init__(self, parent, params: dict, name: str = "all_carriage"):
        """ Creates object parameters for All Carriage class and runs set params method

        :param VSANS parent: The VSANS instance this Beam is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str name: The name of the class
        :return: None as it just sets the parameters
        :rtype: None
        """
        self.parent = parent
        self.name = name

        # In Middle Carriage in the JS
        self.imported_l_1 = 0.0
        self.beam_drop = 0.0  # Also known as Gravity_Drop_Mean in the JS
        self.gravity_drop_min = 0.0
        self.gravity_drop_max = 0.0
        self.beamstop_required = 0.0
        self.beamstop = 0.0
        self.beam_stop_cm = 0.0
        self.two_theta_min = 0.0
        # Values needed for the DQ calculations
        self.overall_dq_calculated = False
        self.dq_geometric = 0.0
        self.dq_wavelength = 0.0
        self.dq_gravity = 0.0
        set_params(instance=self, params=params)

    def _calculate_gravity_drop(self, lambda_val: float = 0.0) -> float:
        """Calculates the gravity drop value from the lambda value, l_1, l_2 and from predefined constants

        :param float lambda_val: The value of lambda gotten from the function running it
        :return: The value that it calculated
        :rtype: Float
        """
        h_over_mn = 395603.0  # Angstrom cm / s
        g = 981.0  # cm/s^2
        return g / 2.0 * math.pow((lambda_val / h_over_mn), 2) * (
                math.pow((self.imported_l_1 + self.parent.get_l_2()), 2) - (
                self.imported_l_1 + self.parent.get_l_2()) * self.imported_l_1)

    def calculate_beam_drop(self):
        """Calculates the beam drop(Or Gravity_Drop_Mean) value from the wavelength and calculate gravity drop"""
        self.beam_drop = self._calculate_gravity_drop(self.parent.get_wavelength())

    def calculate_gravity_drop_min(self):
        """ Calculates the value of gravity drop min from the wavelength and dlambda and calculates using the gravity
        drop method"""
        lambda_val = self.parent.get_wavelength() * (1.0 + self.parent.beam.dlambda)
        self.gravity_drop_min = self._calculate_gravity_drop(lambda_val=lambda_val)

    def calculate_gravity_drop_max(self):
        """ Calculates the value of gravity drop max from the wavelength and dlambda and calculates using the gravity
        drop method"""
        lambda_val = self.parent.get_wavelength() * (1.0 - self.parent.beam.dlambda)
        self.gravity_drop_max = self._calculate_gravity_drop(lambda_val=lambda_val)

    def calculate_beamstop_required(self):
        """Calculates the beamstop required value in CM by calculating the drop min and max and using the values of l_1
            and 2"""
        # Calculate the gravity drops needed for this problem
        self.calculate_gravity_drop_min()
        self.calculate_gravity_drop_max()
        # The actual calculations being done
        beam_size_geometric = self.parent.get_source_aperture() * (self.parent.get_l_2() / self.imported_l_1) + (
                self.parent.get_sample_aperture() * (self.imported_l_1 + self.parent.get_l_2()) / self.imported_l_1)
        gravity_width = abs(self.gravity_drop_max - self.gravity_drop_min)
        beamstop_required = beam_size_geometric + gravity_width
        # UNITS to get into CM
        self.beamstop_required = beamstop_required / 2.54

    def calculate_beam_stop_cm(self):
        """Calculates the beam stop value in CM by diving the value of beamstop by 2.54"""
        self.beam_stop_cm = self.beamstop * 2.54

    def calculate_two_theta_min(self):
        """Calculates the value of two theta min from the beamstop and ssd value"""
        # Fix the calculation of this value???
        self.parent.middle_carriage.calculate_ssd()
        self.two_theta_min = math.atan2(self.beam_stop_cm / 2, self.parent.middle_carriage.ssd)

    def _calculate_dq_geometric(self):
        """Calculates the value of dq_geometric from come constants as well as the sample/source aperture as well as
        l_1 and 2"""
        pixel_size = 0.82  # cm
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow((self.parent.get_l_2() * self.parent.get_source_aperture()) / (4 * self.parent.get_l_1()), 2)
        c = math.pow((self.parent.get_l_1() + self.parent.get_l_2()) * self.parent.get_sample_aperture() / (
                4 * self.parent.get_l_1()), 2)
        d = math.pow(pixel_size / 2, 2) / 3
        self.dq_geometric = a * math.sqrt(b + c + d)

    def _calculate_dq_wavelength(self):
        """Calculates the dq wavelength value from a constants as well as dlambda"""
        resolution_factor = 6.0  # Why is this hard-coded?
        self.dq_wavelength = self.parent.beam.dlambda / math.sqrt(resolution_factor)

    def _calculate_dq_gravity(self):
        """Calculates the dq gravity value from some constants as well as wavelength and l_1 and 2"""
        g = 981.0  # CM/s^2
        h_over_mn = 395603.0  # Angstrom cm/s
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow(g, 2) / (2 * math.pow(h_over_mn, 4))
        c = math.pow(self.parent.get_l_2(), 2) * math.pow(self.parent.get_l_1() + self.parent.get_l_2(), 2)
        d = math.pow(self.parent.get_wavelength(), 4) * 2 / 3 * math.pow(self.parent.beam.dlambda, 2)
        self.dq_gravity = a * math.sqrt(b * c * d)

    def calculate_overall_d_q_values(self):
        """Runs all the calculation methods nessasary to calculate all the dq values and sets the calculated to True"""
        self._calculate_dq_geometric()
        self._calculate_dq_wavelength()
        self._calculate_dq_gravity()
        self.overall_dq_calculated = True

    def calculate_all_Carriage(self):
        """Runs all the calculation methods nessasary to calculate the All Carriage object"""
        self.imported_l_1 = self.parent.get_l_1()
        self.parent.middle_carriage.calculate_L_2()
        self.calculate_beam_drop()
        self.calculate_beamstop_required()  # Also Calls the gravity drop ones too
        self.calculate_beam_stop_cm()
        self.calculate_two_theta_min()
        # Runs more calculation statements
        self.calculate_overall_d_q_values()


class Detector(BaseDetector):
    """ A class for the detector constants needed for calculations

    :param str self.name: The 2 letter name of the detector to use
    :param float self.tube_width: A constant for the tube width
    :param float self.num_tubes: A constant for the number of tubes
    :param float self.num_bins: A constants for the number of bins
    :param float self._coord1_zero_pos:
    :param Method self.x: The method activated when x is called
    :param Method self.y: The method activated when y is called
    :param float self._coord1_ctr_offset: The center offset from corrd 1
    :param float self._coord0_ctr_offset: The center offset form corrd 2
    :param float self.x_dim: The diameter of x
    :param float self.y_dim: The diameter of y
    :param str self.id: The id of the detector
    :param Array self.spatial_calibration: An array that contains special calibration
    :param float self.setback: The value of the detector setback
    :param float self.x_ctr_offset: The center offset of x
    :param float self.y_ctr_offset: The center offset of y
    :param str self.orientation: The orientation of the panel
    :param Boolean self.left_or_bottom: Whether the panel is left/bottom or not
    :param Float self.panel_gap: The gap in between the panel
    """

    def __init__(self, parent, params, where="MR"):
        """ Creates object parameters for Detector class and runs set params method

        :param str where: The location of the pamel
        """
        super().__init__(parent, params)
        self.name = where

        # Default values needed
        self.tube_width = 0.84  # cm
        self.num_tubes = 48
        self.num_bins = 128
        # Other necessary object parameters
        self._coord1_zero_pos = None
        self.x = None
        self.y = None
        self._coord1_ctr_offset = None
        self._coord0_ctr_offset = None
        self.x_dim = None
        self.y_dim = None
        # Constants for this detector that are based on the position of the detector
        self.id = ""
        self.spatial_calibration = []
        self.setback = 0.0
        self.x_ctr_offset = 0.0
        self.y_ctr_offset = 0.0
        self.orientation = ""
        self.left_or_bottom = 0.0
        self.panel_gap = 0.0

        # Set the constant value based on were it is
        self.set_constants()

        # Update the params now that the constants are set
        self.update_params()

    def set_constants(self):
        """Sets all the constant values needed to run this detector"""
        v_spatial_calibration = [-52.1, 0.814, 0]
        h_spatial_calibration = [-26.6, 0.416, 0]

        value_map = {
            "ML": {
                'id': "detector_ML", 'spatial_calibration': v_spatial_calibration, 'setback': 0, 'x_ctr_offset': 0.26,
                'y_ctr_offset': -0.16, 'orientation': 'VERTICAL', 'left_or_bottom': True, 'panel_gap': 0.59
            },
            "MT": {
                'id': "detector_MT", 'spatial_calibration': h_spatial_calibration, 'setback': 41, 'x_ctr_offset': -0.28,
                'y_ctr_offset': 0.6, 'orientation': 'HORIZONTAL', 'left_or_bottom': False, 'panel_gap': 1.83
            },
            "MR": {
                'id': "detector_MR", 'spatial_calibration': v_spatial_calibration, 'setback': 0, 'x_ctr_offset': 0.0,
                'y_ctr_offset': 0.0, 'orientation': 'VERTICAL', 'left_or_bottom': False, 'panel_gap': 0.59
            },
            "MB": {
                'id': "detector_MB", 'spatial_calibration': h_spatial_calibration, 'setback': 41, 'x_ctr_offset': -0.89,
                'y_ctr_offset': 0.96, 'orientation': 'HORIZONTAL', 'left_or_bottom': True, 'panel_gap': 1.83
            },
            "FL": {
                'id': "detector_FL", 'spatial_calibration': v_spatial_calibration, 'setback': 0, 'x_ctr_offset': 0.13,
                'y_ctr_offset': 0.35, 'orientation': 'VERTICAL', 'left_or_bottom': True, 'panel_gap': 0.35
            },
            "FT": {
                'id': "detector_FT", 'spatial_calibration': h_spatial_calibration, 'setback': 41, 'x_ctr_offset': 1.59,
                'y_ctr_offset': 0.33, 'orientation': 'HORIZONTAL', 'left_or_bottom': False, 'panel_gap': 0.33
            },
            "FR": {
                'id': "detector_FR", 'spatial_calibration': v_spatial_calibration, 'setback': 0, 'x_ctr_offset': 0.0,
                'y_ctr_offset': 0.0, 'orientation': 'VERTICAL', 'left_or_bottom': False, 'panel_gap': 0.35
            },
            "FB": {
                'id': "detector_FB", 'spatial_calibration': h_spatial_calibration, 'setback': 41, 'x_ctr_offset': 0.95,
                'y_ctr_offset': 0.95, 'orientation': 'HORIZONTAL', 'left_or_bottom': True, 'panel_gap': 0.33
            },
        }

        vmap = value_map.get(self.name, value_map['MR'])
        self.id = vmap.get('id', f"detector_{self.name}")
        self.spatial_calibration = vmap.get('spatial_calibration', v_spatial_calibration)
        self.setback = vmap.get('setback', 0)
        self.x_ctr_offset = vmap.get('x_ctr_offset', 0.0)
        self.y_ctr_offset = vmap.get('y_ctr_offset', 0.0)
        self.orientation = vmap.get('orientation', "VERTICAL")
        self.left_or_bottom = vmap.get('left_or_bottom', False)
        self.panel_gap = vmap.get('panel_gap', 0.0)

    def update_params(self):
        # Fix the value of this as there are issues with this value

        self._coord1_zero_pos = -(self.panel_gap / 2.0 + (
                self.num_tubes * self.tube_width)) if self.left_or_bottom else self.panel_gap / 2.0
        # The remaining class variables will be set to callable methods to allos other calculations to remain generic
        if self.orientation == 'VERTICAL':
            self.x = self._pixel_to_coord1  # This is a method not a variable
            self.y = self._pixel_to_coord0
            self._coord1_ctr_offset = self.x_ctr_offset
            self._coord0_ctr_offset = self.y_ctr_offset
            self.x_dim = self.num_tubes
            self.y_dim = self.num_bins
        else:
            self.x = self._pixel_to_coord0
            self.y = self._pixel_to_coord1
            self._coord0_ctr_offset = self.x_ctr_offset
            self._coord1_ctr_offset = self.y_ctr_offset
            self.x_dim = self.num_bins
            self.y_dim = self.num_tubes

    def _pixel_to_coord0(self, pixel):
        """A private function that returns a value calculated from the calibration and the offset

        :param float pixel: The value to add to the calculation
        :return: The calculated value
        :rtype: Float
        """
        # convert pixel to spatial dimension, along tube length;
        return self.spatial_calibration[0] - self._coord0_ctr_offset + self.spatial_calibration[1] * pixel + \
            self.spatial_calibration[2] * math.pow(pixel, 2)

    def _pixel_to_coord1(self, pixel):
        """A private function that returns a value calculated from the tube width and the offset

        :param float pixel: The value to add to the calculation
        :return: The calculated value
        :rtype: Float
        """
        return (pixel + 0.5) * self.tube_width + self._coord1_zero_pos - self._coord1_ctr_offset

    def _coord0_to_pixel(self, coord0):
        """A private function that returns a value calculated from the calibration and the offset

        :param float coord0: The value the calculation is subtracted from
        :return: The calculated value
        :rtype: Float
        """
        beta = math.sqrt(self.spatial_calibration[2])
        if beta == 0:
            return (coord0 - self.spatial_calibration[0] + self._coord0_ctr_offset) / self.spatial_calibration[1]
        else:
            alpha = self.spatial_calibration[1] / (2 * beta)
            # pick the right sign?
            return (alpha + math.sqrt(coord0 - self.spatial_calibration[0] + self._coord0_ctr_offset + alpha)) / beta

    def _coord1_to_pixel(self, coord1):
        """A private function that returns a value calculated from the tube width and the offset

        :param float coord1: The value the calculation is subtracted from
        :return: The calculated value
        :rtype: Float
        """
        return (coord1 - self._coord1_zero_pos + self._coord0_ctr_offset) / self.tube_width - 0.5

    def x_min(self, lateral_offset):
        """Calculates and returns the minimum value of x from the x method and lateral offset

        :param float lateral_offset: The offset to include
        :return: The calculated min value of x
        :rtype: Float
        """
        return self.x(0) + (lateral_offset or 0)

    def x_max(self, lateral_offset):
        """Calculates and returns the maximum value of x from the x method, x_dim, and lateral offset

        :param float lateral_offset: The offset to include
        :return: The calculated min value of x
        :rtype: Float
        """
        return self.x(self.x_dim - 1) + (lateral_offset or 0)

    def y_min(self, vertical_offset=None):
        """Calculates and returns the minimum value of y from the y method and lateral offset

        :param float vertical_offset: The offset to include
        :return: The calculated min value of y
        :rtype: Float
        """
        return self.y(0) + (vertical_offset or 0)

    def y_max(self, vertical_offset=None):
        """Calculates and returns the maximum value of y from the y method, y_dim, and lateral offset

        :param float vertical_offset: The offset to include
        :return: The calculated min value of y
        :rtype: Float
        """
        return self.y(self.y_dim - 1) + (vertical_offset or 0)

    def lateral_offset_from_x_max(self, x):
        """Gets the lateral offset of x_max from x_max by subtracting x and x_max

        :param float x: The value of x to subtract from
        :return: The value calculated
        :rtype: Float
        """
        return x - self.x_max(0)

    def lateral_offset_from_x_min(self, x):
        """Gets the lateral offset of x_min from x_min by subtracting x and x_min

        :param float x: The value of x to subtract from
        :return: The value calculated
        :rtype: Float
        """
        return x - self.x_min(0)

    def vertical_offset_from_y_max(self, y):
        """Gets the lateral offset of y_max from y_max by subtracting y and y_max

        :param float y: The value of y to subtract from
        :return: The value calculated
        :rtype: Float
        """
        return y - self.y_max(0)

    def vertical_offset_from_y_min(self, y):
        """Gets the lateral offset of y_min from y_min by subtracting y and y_min

        :param float y: The value of y to subtract from
        :return: The value calculated
        :rtype: Float
        """
        return y - self.y_min(0)


class Carriage:
    """A class for storing and manipulating Carriage related data and objects

    :param VSANS self.parent: The parent VSANS object
    :param VerticalPanel self.left_panel: A vertical panel object that represents the left panel
    :param VerticalPanel self.right_panel: A vertical panel object that represents the right panel
    :param HorizontalPanel self.top_panel: A horizontal panel object that represents the top panel
    :param HorizontalPanel self.bottom_panel: A horizontal panel object that represents the bottom panel
    :param DqCalculator self.dq_calc: The DqCalculator object to calculate all the DQ value
    :param float self.ssd_input: The ssd value inputted by the user into the JS
    :param float self.ssd: The calculated value of SSD
    :param float self.l_2: The calculated value of l_2
    :param float self.refBeamCtr_x: The reference center X
    :param float self.refBeamCtr_y: The reference center Y
    :param float self.lr_w: The Left Right Panel width
    :param float self.lr_h: The Left Right Panel height
    :param float self.tb_w: The Top Bottom Panel width
    :param float self.tb_h: The Top Bottom Panel height
    :param float self.ssd_setback: The ssd setback value for the middle
    """
    def __init__(self, parent: Instrument, params: dict, name: str = "middle_carriage"):
        """ Creates sub object and object parameters for Middle Carriage class and runs set params method

        :param parent: The VSANS Instrument instance this Carriage is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str name: The detector carriage name (not the class name)
        """
        self.parent = parent
        self.name = name
        self.left_panel = None
        self.right_panel = None
        self.top_panel = None
        self.bottom_panel = None
        self.dq_calc = None

        # Creates all the necessary parameters for the middle carriage class
        self.ssd_input = 0.0
        self.ssd = 0.0
        self.l_2 = 0.0

        # DQ Values that are used for both classes
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0

        # Front detector dimensions
        self.lr_w = 0.0
        self.lr_h = 0.0
        self.tb_w = 0.0
        self.tb_h = 0.0
        self.ssd_setback = 0.0

    def calculate_ssd(self):
        """Calculates the SSD value from the ssd JS value and sample to gv"""
        self.ssd = self.ssd_input + self.parent.collimation.sample_to_gv

    def calculate_L_2(self):
        """Calculates the value of l_2 from the ssd JS value and the sample to ap_gv"""
        self.l_2 = self.ssd_input + self.parent.collimation.sample_to_ap_gv

    def calculate_carriage(self):
        """Runs all the calculation methods nessasary to calculate the Middle Carriage object and sub objects"""
        # Calculates all the parameters of this object
        self.calculate_ssd()
        self.calculate_L_2()
        # Calculates the 2 other panels
        self.left_panel.calculate_panel()
        self.right_panel.calculate_panel()
        self.top_panel.calculate_panel()
        self.bottom_panel.calculate_panel()
        self.dq_calc.calculate_all_dq()


class Panel:
    """A class for storing and manipulating detector panel related data.

        :param FrontCarriage or MiddleCarriage self.parent: The parent FrontCarriage or MiddleCarriage object
        :param str self.name: The name of the class
        :param str self.short_name: The short name for this panel (First letter is carriage)(Second Letter is Panel
            Position)
        :param Boolean self.horizontal_orientation: A boolean whether the panel is horizontal or vertical
        :param float self.offset: The offset set the user relative to the paired detector
        :param float self.qx_min: The min value of qx
        :param float self.qx_max: The max value of qx
        :param float self.qy_min: The min value of qy
        :param float self.qy_max: The max value of qy
        :param float self.refBeamCtr_x: The amount the panel assembly is off in the x direction(From Parent Class)
        :param float self.refBeamCtr_y: The amount the panel assembly is off in the y direction(From Parent Class)
        :param Boolean self.is_valid: Is this a valid position of it
        :param Boolean self.match_button: Whether the match checkbox is checked or not
        :param Detector self.detectors: The detector object for this specific panel position
        :param float self.x_pixel_size: The size of the panel in cm
        :param float self.y_pixel_size: The size of the panel in pixels
        :param float self.pixel_num_x: The number of x pixels in the panel
        :param float self.pixel_num_y: The number of y pixels in the panel
        :param float self.beam_center_x: The location of the center x coordinate
        :param float self.beam_center_y: The location of the center y coordinate
        :param float self.beam_center_x_pix: The location of the x beam center in pixels
        :param float self.beam_center_y_pix: The location of the y beam center in pixels
        :param Array self.data: The data array needed for the calculations of plots
        :param Array self.detector_array: The array of data needed for calculation of plot
        :param Array self.q_to_t_array: An array of q to t values
        :param Array self.qx_array: An array of the qx values
        :param Array self.qy_array: An array of the qy values
        :param Array self.qz_array: An array of the qz values
        :param Array self.default_mask: An array containing the default  mask
        :param Array self.data_real_dist_x: An array containing the data_real distance x
        :param Array self.data_real_dist_y: An array containing the data_real distance y
        """

    def __init__(self, parent: Carriage, params: dict, short_name: str = "MR"):
        """ Creates object parameters for VerticalPanel class and runs set params method

        :param FrontCarriage or MiddleCarriage parent: The FrontCarriage or MiddleCarriage instance this is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param short_name: A one or two character short name of the detector panel of the form (F|M|B)(T|B|L|R| )
        """
        self.parent = parent
        self.name = self.__class__.__name__
        self.short_name = short_name
        self.horizontal_orientation = False
        self.offset = 0.0
        self.qx_min = 0.0  # Left
        self.qx_max = 0.0  # Right
        self.qy_min = 0.0  # Bottom
        self.qy_max = 0.0  # Top
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0
        self.is_valid = False
        self.k_bctr_cm = True
        self.match_button = None
        self.detectors = Detector(parent, params, short_name)

        # Constants needed for plotting
        self.x_pixel_size = 0.0
        self.y_pixel_size = 0.0
        self.pixel_num_x = 0
        self.pixel_num_y = 0
        self.beam_center_x = 0.0
        self.beam_center_y = 0.0
        self.beam_center_x_pix = 0.0
        self.beam_center_y_pix = 0.0
        self.setback = 0.0
        self.tmp_calib = [-512, 8, 0]

        # Detector Arrays
        self.data = None
        self.detector_array = None
        self.q_to_t_array = None
        self.qx_array = None
        self.qy_array = None
        self.qz_array = None
        self.default_mask = None
        self.data_real_dist_x = None  # data_realDistX
        self.data_real_dist_y = None  # data_realDistY
        # Calculated Arrays
        self.dx = None
        self.dy = None
        self.phi = None
        self.two_theta = None

        set_params(instance=self, params=params)

    def calculate_match(self):
        """If the match button is true set it to match correctly and set its return to disable the lateral offset
            field and if not enable the vertical offset field"""
        if self.match_button is not None:
            if self.match_button:
                self._calculate_match()
                self.parent.parent.options[self.name + "_offset"] = {"type": "readonly", "set_to": True}
            else:
                pass

    def _calculate_match(self):
        """Pseudo-Abstract method: Child Classes must implement or error will be thrown."""
        raise NotImplementedError

    def _calculate_q_helper(self, value: np.ndarray | float) -> np.ndarray | float:
        """A help function that helps to calculate the q min and max values by using the wavelength and ssd

        :param float value: The value given to the function that allows it ot run
        :return: The calculated value
        :rtype: Float
        """
        return 4 * np.pi / self.parent.parent.get_wavelength() * np.sin(
            np.atan2(value, self.parent.ssd + self.detectors.setback) / 2)

    def create_detector_array(self):
        """Creates 5 arrays of zeros based on the number of x and y pixels"""
        self.detector_array = np.zeros((self.pixel_num_x, self.pixel_num_y))
        self.q_to_t_array = np.zeros((self.pixel_num_x, self.pixel_num_y))
        self.qx_array = np.zeros((self.pixel_num_x, self.pixel_num_y))
        self.qy_array = np.zeros((self.pixel_num_x, self.pixel_num_y))
        self.qz_array = np.zeros((self.pixel_num_x, self.pixel_num_y))
        self.data_real_dist_x = np.ones((self.pixel_num_x, self.pixel_num_y))
        self.data_real_dist_y = np.ones((self.pixel_num_x, self.pixel_num_y))
        self.data = np.zeros((self.pixel_num_x, self.pixel_num_y))

    def calculate_panel(self):
        """Runs all the calculation methods necessary to calculate the panel object without the plots"""
        self.refBeamCtr_x = self.parent.refBeamCtr_x
        self.refBeamCtr_y = self.parent.refBeamCtr_y
        self.calculate_match()  # This needs to run first as it affects the values for the rest of the calculations

    def fill_panel_w_ones(self):
        """Takes the specified panel object and added model data to the data parameter based on some parameters and
        then runs detector_2q_non_linear"""
        IMON = 1e+11
        TRANS = 0.8
        THICK = 0.1
        ssd = self.parent.ssd
        # Get the setback value of each part
        ssd = ssd + self.setback
        pix_size_x = self.x_pixel_size
        pix_size_y = self.y_pixel_size

        tmp_inten = np.ones(self.q_to_t_array.shape)
        # Id not implement if add_emp_bgd ad it did not seem necessary without model application
        # I also did not implement if back detector as we do not have the back director at this time
        tmp_inten *= TRANS * THICK * pix_size_x * pix_size_y / np.pow(ssd, 2)
        tmp_inten *= IMON
        tmp_inten = np.sqrt(tmp_inten)
        tmp_inten = np.random.normal(tmp_inten)
        self.detector_array = tmp_inten / (TRANS * THICK * pix_size_x * pix_size_y / np.pow(ssd, 2) * IMON)

    def plot_panel(self):
        """Creates the data_real_dist_x and data_real_dist_y arrays and then runs detector_2q_non_linear"""
        self.make_real_dist_x_y_waves()
        m_sep = self.offset
        pix_size_x = self.x_pixel_size
        pix_size_y = self.y_pixel_size
        n_pixels_x = int(self.pixel_num_x)
        n_pixels_y = int(self.pixel_num_y)
        self.beam_center_x_pix = n_pixels_x - (m_sep / pix_size_x)
        self.beam_center_y_pix = n_pixels_y / 2

        if self.k_bctr_cm:
            data_real_dist_x = self.data_real_dist_x
            data_real_dist_y = self.data_real_dist_y
            self.beam_center_x_pix = (data_real_dist_x[n_pixels_x - 1][0] / 10 + (
                    self.beam_center_x_pix - n_pixels_x - 1) * pix_size_x)
            self.beam_center_y_pix = data_real_dist_y[0][int(self.beam_center_y_pix)] / 10
        self.detector_2q_non_linear()  # Something to set scale

    def detector_2q_non_linear(self):
        """Calculates the q_to_t_array, qx_array, qy_array, and qy_array

        :param HorizontalPanel or VerticalPanel panel_object: The object that the methods are being set on
        :return: None as it just sets of values of many arrays
        :rtype: None
        """
        self.dx = np.asarray(self.data_real_dist_x) - self.pixel_num_x
        self.dy = np.asarray(self.data_real_dist_y) - self.pixel_num_y
        self.phi = np.arctan2(self.dy, self.dx)
        dist = np.sqrt(np.pow(self.dx, 2) + np.sqrt(np.pow(self.dy, 2)))
        dist = dist / 10
        self.two_theta = np.atan(dist / self.parent.ssd)
        self.q_to_t_array = (4 * np.pi / self.parent.parent.get_wavelength()) * np.sin(self.two_theta / 2)
        self.qx_array = self.q_to_t_array * np.cos(self.two_theta / 2) * np.cos(self.phi)
        self.qy_array = self.q_to_t_array * np.cos(self.two_theta / 2) * np.sin(self.phi)
        self.qz_array = self.q_to_t_array * np.sqrt(self.two_theta / 2)

    def make_real_dist_x_y_waves(self):
        """Updates the other_array_x and other_array_y arrays based on the orientation of the panel and the gap

        VC_MakeRealDistXYWaves in IGORPro

        :param HorizontalPanel or VerticalPanel panel_object: The panel that the calculations are being done on
        :return: Nothing as it just runs calculations and sets values
        :rtype: None
        """
        # make the data_realDistX,Y Waves that are needed for the calculation of q
        tmp_array = self.tmp_calib
        tube_width = 8.4
        # self.non_linear_correction(data,tmpCalib,tube_width,detStr,destPath)

        # The below is V_NonLinearCorrection in igor
        horizontal_orientation = self.horizontal_orientation
        diamX = len(self.detector_array)
        diamy = len(self.detector_array[0])
        # Find the panel gap from the list of constants
        if 'F' in self.short_name:
            if not horizontal_orientation:
                gap = 3.5
            else:
                gap = 3.3
        elif 'M' in self.short_name:
            if not horizontal_orientation:
                gap = 5.9
            else:
                gap = 18.3
        else:
            gap = 0.0

        # Params needed to calculate teh real_dist arrays
        self.data_real_dist_x = np.asarray(self.data_real_dist_x)
        self.data_real_dist_y = np.asarray(self.data_real_dist_y)
        offset = self.offset * 10

        # Get the data in the real_dist arrays
        if not horizontal_orientation:
            if self.k_bctr_cm:  # Matches what is in IGOR:
                if 'L' in self.short_name:
                    self.data_real_dist_x = offset - (diamX - self.data_real_dist_x - .5) * tube_width - gap / 2
                else:  # Matches what is in IGOR
                    # If it is on the right
                    self.data_real_dist_x = tube_width * (self.data_real_dist_x + .5) + offset + gap / 2
            else:
                self.data_real_dist_x *= tube_width
            # Set up the y array for the horizontal orientation
            self.data_real_dist_x = (tmp_array[0] + tmp_array[1] * self.data_real_dist_x +
                                     tmp_array[2] * self.data_real_dist_x * self.data_real_dist_x)
        else:  # If it is a horizontal panel
            if self.k_bctr_cm:
                if 'T' in self.short_name:
                    self.data_real_dist_y = tube_width * (self.data_real_dist_y + .5) + offset + gap / 2
                else:
                    self.data_real_dist_y = offset - (diamy - self.data_real_dist_y - .5) * tube_width - gap / 2
            else:
                self.data_real_dist_y = tube_width * self.data_real_dist_y
            self.data_real_dist_x = (tmp_array[0] + tmp_array[1] * self.data_real_dist_x +
                                     tmp_array[2] * self.data_real_dist_x * self.data_real_dist_x)

    def draw_mask(self):
        """Creates the mask based on the given panel object"""
        # DEVNotes- this is where I stopped

        offset = self.offset
        D2 = self.parent.parent.get_sample_aperture()
        l2 = self.parent.l_2
        # TODO: Finish me!


class VerticalPanel(Panel):
    """A class for storing and manipulating VerticalPanel related data based on the generic Panel class.

    This is used for left and right panel data"""
    def __init__(self, parent: Carriage, params: dict, short_name: str = "MR"):
        """ Creates object parameters for VerticalPanel class and runs set params method

        :param FrontCarriage or MiddleCarriage parent: The FrontCarriage or MiddleCarriage instance this is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str short_name: A one or two character short name of the detector panel of the form (F|M|B)(T|B|L|R| )
        """
        super().__init__(parent, params, short_name)
        self.horizontal_orientation = False

        # Constants needed for plotting
        self.x_pixel_size = 0.84
        self.y_pixel_size = 0.8
        self.pixel_num_x = 48
        self.pixel_num_y = 128
        self.tmp_calib = [-512, 8, 0]

    def _calculate_match(self):
        """If the match button is true set it to match correctly and set its return to disable the lateral offset
        field and if not enable the lateral offset field"""
        if self.short_name.find("L") != -1:
            self._calculate_match_left()
        else:
            self._calculate_match_right()

    def _calculate_match_left(self):
        """Calculates how to match the front panel selected to  the left side using the middle lateral offset ssd and
        center as well as the front center ssd"""
        middle_object = self.parent.parent.middle_carriage
        xmin = middle_object.left_panel.detectors.x_min(
            middle_object.left_panel.offset) - middle_object.refBeamCtr_x
        angle_min = math.atan2(xmin, middle_object.ssd)
        fr_xmax = math.tan(angle_min) * self.parent.ssd + self.refBeamCtr_x
        self.offset = self.detectors.lateral_offset_from_x_max(fr_xmax)

    def _calculate_match_right(self):
        """Calculates how to match the front panel selected to the right side using the middle lateral offset ssd and
        center as well as the front center ssd"""
        middle_object = self.parent.parent.middle_carriage
        xmax = middle_object.right_panel.detectors.x_max(
            middle_object.right_panel.offset) - middle_object.refBeamCtr_x
        angle_max = math.atan2(xmax, middle_object.ssd)
        fr_xmin = math.tan(angle_max) * self.parent.ssd + self.refBeamCtr_x
        self.offset = self.detectors.lateral_offset_from_x_min(fr_xmin)

    def calculate_qx_min(self):
        """Calculates the qx min of this detector using the lateral offset and center into the _x_min function from
        the detector object"""
        self.qx_min = self._calculate_q_helper(self.detectors.x_min(self.offset) - self.refBeamCtr_x)

    def calculate_qx_max(self):
        """Calculates the qx max of this detector using the lateral offset and center into the _x_min function from the
        detector object"""
        self.qx_max = self._calculate_q_helper(self.detectors.x_max(self.offset) - self.refBeamCtr_x)

    def calculate_qy_min(self):
        """Calculates the qy min of this detector using the lateral offset and center into the _y_min function from
        the detector object"""
        self.qy_min = self._calculate_q_helper(self.detectors.y_min() - self.refBeamCtr_y)

    def calculate_qy_max(self):
        """Calculates the qy max of this detector using the lateral offset and center into the _y_max function from
        the detector object"""
        self.qy_max = self._calculate_q_helper(self.detectors.y_max() - self.refBeamCtr_y)

    def create_default_mask(self):
        """ Creates the default mask defending on the orientation of the panel"""
        if 'L' in self.short_name:
            inner_array = np.concatenate((np.ones(5), np.zeros(118), np.ones(5)))
            self.default_mask = np.concatenate((np.zeros((4, 128)), np.tile(inner_array, (44, 1))))
        else:
            inner_array = np.concatenate((np.ones(5), np.zeros(118), np.ones(5)))
            self.default_mask = np.concatenate((np.tile(inner_array, (44, 1)), np.zeros((4, 128))))

    def calculate_panel(self):
        """Runs all the calculation methods nessasary to calculate the panel object without the plots"""
        super().calculate_panel()
        self.calculate_qx_min()
        self.calculate_qx_max()
        self.calculate_qy_min()
        self.calculate_qy_max()


class HorizontalPanel(Panel):
    """A class for storing and manipulating HorizontalPanel related data based on the generic Panel class.

    This is used for top and bottom panel data"""
    def __init__(self, parent: Carriage, params: dict, short_name: str = "FT"):
        """ Creates object parameters for HorizontalPanel class and runs set params method

        :param FrontCarriage or MiddleCarriage parent: The FrontCarriage or MiddleCarriage instance this is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param short_name: A one or two character short name of the detector panel of the form (F|M|B)(T|B|L|R| )
        """
        super().__init__(parent, params, short_name)
        self.horizontal_orientation = True

        # Constants needed for plotting
        self.x_pixel_size = 0.4  # Along the horizontal tubes (VCALC: x_pixel_size = 0.4 cm)
        self.y_pixel_size = 0.84
        self.pixel_num_x = 128
        self.pixel_num_y = 48
        self.setback = 41
        self.tmp_calib = [-256, 4, 0]

    def _calculate_match(self):
        """If the match button is true set it to match correctly and set its return to disable the lateral offset
        field and if not enable the lateral offset field"""
        if self.short_name.find("T") != -1:
            self._calculate_match_top()
        else:
            self._calculate_match_bottom()

    def _calculate_match_bottom(self):
        """Calculates how to match the front panel selected to  the bottom side using the middle vertical offset ssd and
        center as well as the front center ssd"""
        middle_object = self.parent.parent.middle_carriage
        ymin = middle_object.right_panel.detectors.y_min(0) - middle_object.refBeamCtr_y
        angle_min = math.atan2(ymin, middle_object.ssd)
        fr_ymax = math.tan(angle_min) * (self.parent.ssd + self.detectors.setback) + self.refBeamCtr_y
        self.offset = self.detectors.vertical_offset_from_y_max(fr_ymax)

    def _calculate_match_top(self):
        """Calculates how to match the front panel selected to the right side using the middle vertical offset ssd and
        center as well as the front center ssd"""
        middle_object = self.parent.parent.middle_carriage
        ymax = middle_object.right_panel.detectors.y_max(0) - middle_object.refBeamCtr_y
        angle_max = math.atan2(ymax, middle_object.ssd)
        fr_ymin = math.tan(angle_max) * (self.parent.ssd + self.detectors.setback) + self.refBeamCtr_y
        self.offset = self.detectors.vertical_offset_from_y_min(fr_ymin)

    def calculate_qy_min(self):
        """Calculates the qy min of this detector using the lateral offset and center into the _y_min function from
        the detector object"""
        self.qy_min = self._calculate_q_helper(self.detectors.y_min(self.offset) - self.refBeamCtr_y)

    def calculate_qy_max(self):
        """Calculates the qy max of this detector using the lateral offset and center into the _y_max function from
        the detector object"""
        self.qy_max = self._calculate_q_helper(self.detectors.y_max(self.offset) - self.refBeamCtr_y)

    def create_default_mask(self):
        """ Creates the default mask defending on the orientation of the panel"""
        self.default_mask = np.concatenate((np.ones((50, 48)), np.zeros((28, 48)), np.ones((50, 48))))

    def calculate_panel(self):
        """Runs all the calculation methods necessary to calculate the panel object without the plots"""
        super().calculate_panel()
        self.calculate_qy_min()
        self.calculate_qy_max()


class MiddleCarriage(Carriage):
    """A class for storing and manipulating Middle Carriage related data and objects"""
    def __init__(self, parent: Instrument, params: dict, name: str = "middle_carriage"):
        """ Creates sub object and object parameters for Middle Carriage class and runs set params method"""
        super().__init__(parent, params, name)
        # Create the secondary object off the main object
        self.left_panel = VerticalPanel(self, params.get("mid_left_panel", {}), short_name="ML")
        self.right_panel = VerticalPanel(self, params.get("mid_right_panel", {}), short_name="MR")
        self.top_panel = HorizontalPanel(self, params.get("mid_top_panel", {}), short_name="MT")
        self.bottom_panel = HorizontalPanel(self, params.get("mid_bottom_panel", {}), short_name="MB")
        self.dq_calc = DqCalculator(self, params.get("mid_dq_values", {}))
        carriage_params = params.get("middle_carriage", {})
        set_params(instance=self, params=carriage_params)


class FrontCarriage(Carriage):
    """A class for storing and manipulating Middle Carriage related data and objects"""
    def __init__(self, parent: Instrument, params: dict, name: str = "front_carriage"):
        """ Creates sub object and object parameters for Middle Carriage class and runs set params method"""
        super().__init__(parent, params, name)
        self.left_panel = VerticalPanel(self, params.get("front_left_panel", {}), short_name="FL")
        self.right_panel = VerticalPanel(self, params.get("front_right_panel", {}), short_name="FR")
        self.top_panel = HorizontalPanel(self, params.get("front_top_panel", {}), short_name="FT")
        self.bottom_panel = HorizontalPanel(self, params.get("front_bottom_panel", {}), short_name="FB")
        self.dq_calc = DqCalculator(self, params.get("front_dq_values", {}))
        carriage_params = params.get("front_carriage", {})
        set_params(instance=self, params=carriage_params)