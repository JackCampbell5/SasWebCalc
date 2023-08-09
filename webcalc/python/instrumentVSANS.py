from .instrument import set_params
import math
import numpy as np


class Beam:
    def __init__(self, parent, params, name="beam"):
        self.parent = parent
        self.wavelength = 0  # Known as lamda in the js
        self.dlambda = 0.0
        self.lambda_T = 0.0
        self.phi_0 = 0.0
        self.frontend_trans = 0.0
        self.flux = 0.0
        self.beam_current = 0.0
        self.i_sub_zero = 0.0  # or Incident_Intensity
        self.frontend_trans_options = {}
        self.name = name
        set_params(instance=self, params=params)

    def dlambda_check_lambda(self):
        """ Makes sure the value of wavelength is correct based off dlambda

        :return:
        """
        if self.dlambda == 0.02:
            self.wavelength = 4.75
        elif self.dlambda == 0.4:
            self.wavelength = 5.3

    def calculate_wavelength(self):
        """If the value of the wavelength is in the wrong range brings it to the correct range

        """
        self.dlambda_check_lambda()
        if self.wavelength < 4:
            self.wavelength = 4.0
        elif 8.5 < self.wavelength < 10.7:
            self.wavelength = 8.5
        elif self.wavelength > 19.3:
            self.wavelength = 19.3

    def calculate_frontend_trans(self):
        """Gets the value of frontend_trans from the list of options based on dlambda"""
        self.frontend_trans = self.frontend_trans_options[str(self.dlambda)]

    def calculate_flux(self):
        lfrac = self.lambda_T / self.wavelength
        self.flux = (self.dlambda * math.pow(lfrac, 4) * math.exp(-math.pow(lfrac, 2)) * self.phi_0) / 2.0 * math.pi

    def calculate_beam_current(self):
        self.parent.collimation.calculate_t_filter()
        t_filter = self.parent.collimation.t_filter
        self.beam_current = self.frontend_trans * t_filter

    def calculate_iSub0(self):
        collimation = self.parent.collimation
        collimation.calculate_sample_aperture()
        self.i_sub_zero = self.beam_current / (math.pi * math.pow(collimation.sample_aperture / 2.0, 2))

    def calculate_beam(self):
        self.calculate_wavelength()
        self.calculate_frontend_trans()
        self.calculate_flux()
        self.calculate_beam_current()
        self.calculate_iSub0()


class Collimation:
    def __init__(self, parent, params, name="collimation"):
        self.parent = parent
        self.name = name
        self.guide_select = 0
        self.num_guides = 0  # No calculation necessary just get the value
        self.cov_beams = False
        self.source_aperture_js = 0.0  # The one coming from the js ( No Calculation Necessary)
        self.source_aperture = 0.0  # The one that is used for the calculations
        self.source_distance = 0.0
        self.source_distance_options = [2441, 2157, 1976, 1782, 1582, 1381, 1181, 980, 780, 579]
        self.t_filter = 0.0
        self.t_guide = 0.0
        self.sample_aperture = 0.0
        self.ext_sample_aperture = 0.0  # This is a constant and does not need to be calculated
        self.sample_to_ap_gv = 0.0
        self.sample_to_gv = 0.0
        self.l_1 = 0.0
        self.a_over_l = 0.0

        set_params(instance=self, params=params)

    def calculate_num_guides(self):
        self.num_guides = 0 if self.guide_select == "CONV_BEAMS" or self.guide_select == "NARROW_SLITS" else int(
            self.guide_select)

    def calculate_source_aperture(self):
        """Calculates the value of the source aperture

        :return: None as it just sets a value
        """
        self.source_aperture = float(self.source_aperture_js) / 10.0

    def calculate_sourceDistance(self):
        self.source_distance = self.source_distance_options[self.num_guides]

    def calculate_t_filter(self):
        # Calculation run in beam.calculate_beam_current()
        lambda_val = self.parent.get_wavelength()
        self.t_filter = math.exp(-0.371 - 0.0305 * lambda_val - 0.00352 * math.pow(lambda_val, 2))

    def calculate_t_guide(self):
        return math.pow(0.97, self.num_guides)

    def calculate_sample_aperture(self):
        self.sample_aperture = self.ext_sample_aperture / 10.0

    def calculate_l_1(self):
        self.l_1 = self.source_distance - self.sample_to_ap_gv

    def calculate_aOverL(self):
        self.a_over_l = math.pow((math.pi / 4.0 * self.source_aperture * self.sample_aperture / self.l_1), 2)

    def calculate_collimation(self):
        self.calculate_num_guides()
        self.calculate_source_aperture()
        self.calculate_sourceDistance()
        self.calculate_t_guide()
        self.calculate_sample_aperture()
        self.calculate_l_1()
        self.calculate_aOverL()


class AllCarriage:
    def __init__(self, parent, params, name="all_carriage"):
        self.parent = parent
        self.name = name

        # In Middle Carriage in the JS
        self.imported_l_1 = 0.0
        self.beam_drop = 0.0  # Also know as Gravity_Drop_Mean in the JS
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

    def calculate_beam_drop(self):
        # Also known as Gravity_Drop_Mean in the JS
        lambda_val = self.parent.get_wavelength()
        self.beam_drop = self._calculate_gravity_drop(lambda_val=lambda_val)

    def _calculate_gravity_drop(self, lambda_val=0.0):
        h_over_mn = 395603.0  # Angstrom cm / s
        g = 981.0  # cm/s^2
        return g / 2.0 * math.pow((lambda_val / h_over_mn), 2) * (
                math.pow((self.imported_l_1 + self.parent.get_l_2()), 2) - (self.imported_l_1 + self.parent.get_l_2()) *
                self.imported_l_1)

    def calculate_gravity_drop_min(self):
        #         var lambda = this.lambda * (1.0 + this.dlambda);
        lambda_val = self.parent.get_wavelength() * (1.0 + self.parent.beam.dlambda)
        self.gravity_drop_min = self._calculate_gravity_drop(lambda_val=lambda_val)

    def calculate_gravity_drop_max(self):
        lambda_val = self.parent.get_wavelength() * (1.0 - self.parent.beam.dlambda)
        self.gravity_drop_max = self._calculate_gravity_drop(lambda_val=lambda_val)

    def calculate_beamstop_required(self):
        # Calculate the gravity drops needed for this problem
        self.calculate_gravity_drop_min()
        self.calculate_gravity_drop_max()
        # The actual calculations being done
        beam_size_geometric = self.parent.get_source_aperture() * self.parent.get_l_2() / self.imported_l_1 + \
                              self.parent.get_sample_aperture() * (
                self.imported_l_1 + self.parent.get_l_2()) / self.imported_l_1
        gravity_width = abs(self.gravity_drop_max - self.gravity_drop_min)
        beamstopRequired = beam_size_geometric + gravity_width
        # UNITS to get into CM
        self.beamstop_required = beamstopRequired / 2.54

    def calculate_beam_stop_cm(self):
        self.beam_stop_cm = self.beamstop * 2.54

    def calculate_θ2_min(self):
        # Also known as TwoTheta_min
        # FIx the calculation of this value
        self.parent.middle_carriage.calculate_ssd()
        self.two_theta_min = math.atan2(self.beam_stop_cm / 2, self.parent.middle_carriage.ssd)

    def calculate_overall_d_q_values(self):
        self._calculate_dq_geometric()
        self._calculate_dq_wavelength()
        self._calculate_dq_gravity()
        self.overall_dq_calculated = True

    def _calculate_dq_geometric(self):
        pixel_size = 0.82  # cm
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow((self.parent.get_l_2() * self.parent.get_source_aperture()) / (4 * self.parent.get_l_1()), 2)
        c = math.pow((self.parent.get_l_1() + self.parent.get_l_2()) * self.parent.get_sample_aperture() / (
                4 * self.parent.get_l_1()), 2)
        d = math.pow(pixel_size / 2, 2) / 3
        self.dq_geometric = a * math.sqrt(b + c + d)

    def _calculate_dq_wavelength(self):
        resolution_factor = 6.0
        self.dq_wavelength = self.parent.beam.dlambda / math.sqrt(resolution_factor)

    def _calculate_dq_gravity(self):
        g = 981.0  # CM/s^2
        h_over_mn = 395603.0  # Angstrom cm/s
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow(g, 2) / (2 * math.pow(h_over_mn, 4))
        c = math.pow(self.parent.get_l_2(), 2) * math.pow(self.parent.get_l_1() + self.parent.get_l_2(), 2)
        d = math.pow(self.parent.get_wavelength(), 4) * 2 / 3 * math.pow(self.parent.beam.dlambda, 2)
        self.dq_gravity = a * math.sqrt(b * c * d)

    def calculate_all_Carriage(self):
        self.imported_l_1 = self.parent.get_l_1()
        self.parent.middle_carriage.calculate_L_2()
        self.calculate_beam_drop()
        self.calculate_beamstop_required()  # Also Calls the gravity drop ones too
        self.calculate_beam_stop_cm()
        self.calculate_θ2_min()
        # Runs more calculation statements
        self.calculate_overall_d_q_values()


class MiddleCarriage:
    def __init__(self, parent, params, name="middle_carriage"):
        self.parent = parent
        self.name = name

        # Create the secondary object off the main object
        self.left_panel = VerticalPanel(self, params.get("mid_left_panel", {}), name="mid_left_panel", short_name="ML")
        self.right_panel = VerticalPanel(self, params.get("mid_right_panel", {}), name="mid_right_panel",
                                         short_name="MR")
        self.top_panel = HorizontalPanel(self, params.get("mid_top_panel", {}), name="front_top_panel", short_name="MT")
        self.bottom_panel = HorizontalPanel(self, params.get("mid_bottom_panel", {}), name="front_bottom_panel",
                                            short_name="MB")
        self.dq_calc = DqCalculator(self, params.get("mid_dq_values", {}))

        params = params.get("middle_carriage", {})

        # Creates all the necessary parameters for the middle carriage class
        self.ssd_input = 0.0  # This is just the value input by the user, not the actual SSD value
        self.ssd = 0.0
        self.l_2 = 0.0
        # DQ Values that are used for both classes
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0

        # Front detector dimensions
        self.middle_lr_w = 0.0
        self.middle_lr_h = 0.0
        self.middle_tb_w = 0.0
        self.middle_tb_h = 0.0
        self.middle_ssd_setback = 0.0

        set_params(instance=self, params=params)

    def calculate_ssd(self):
        self.ssd = self.ssd_input + self.parent.collimation.sample_to_gv

    # create a class for the chnaging dq values and the constant calculated values are kept in the front apature clas
    # sbut there is a paramater that will be set saying the calculations can be done in the dependet classes

    def calculate_L_2(self):
        self.l_2 = self.ssd_input + self.parent.collimation.sample_to_ap_gv

    def calculate_middleCarriage(self):
        # Calculates all the parameters of this object
        self.calculate_ssd()
        # Calculates the 2 other panels
        self.left_panel.calculate_panel()
        self.right_panel.calculate_panel()
        self.top_panel.calculate_panel()
        self.bottom_panel.calculate_panel()
        self.dq_calc.calculate_all_dq()


class FrontCarriage:
    def __init__(self, parent, params, name="front_carriage"):
        self.parent = parent
        self.name = name
        # Create the secondary object off the main object
        self.left_panel = VerticalPanel(self, params.get("front_left_panel", {}), name="front_left_panel",
                                        short_name="FL")
        self.right_panel = VerticalPanel(self, params.get("front_right_panel", {}), name="front_right_panel",
                                         short_name="FR")
        self.top_panel = HorizontalPanel(self, params.get("front_top_panel", {}), name="front_top_panel",
                                         short_name="FT")
        self.bottom_panel = HorizontalPanel(self, params.get("front_bottom_panel", {}), name="front_bottom_panel",
                                            short_name="FB")
        self.dq_calc = DqCalculator(self, params.get("front_dq_values", {}))
        params = params.get("front_carriage", {})

        # Creates all the necessary parameters for the Front carriage class
        self.ssd_input = 0.0
        self.ssd = 0.0
        self.l_2 = 0.0
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0

        # Front detector dimensions
        self.front_lr_w = 0.0
        self.front_lr_h = 0.0
        self.front_tb_w = 0.0
        self.front_tb_h = 0.0
        self.front_ssd_setback = 0.0

        set_params(instance=self, params=params)

    def calculate_ssd(self):
        self.ssd = self.ssd_input + self.parent.collimation.sample_to_gv

    def calculate_L_2(self):
        self.l_2 = self.ssd_input + self.parent.collimation.sample_to_ap_gv

    def calculate_frontCarriage(self):
        self.calculate_ssd()
        self.calculate_L_2()
        # Calculate the other objects
        self.left_panel.calculate_panel()
        self.right_panel.calculate_panel()
        self.top_panel.calculate_panel()
        self.bottom_panel.calculate_panel()
        self.dq_calc.calculate_all_dq()


class DqCalculator:
    def __init__(self, parent, params, name="DqCalculator"):
        self.parent = parent
        self.name = name

        self.q_min = 0.0
        self.calculate_q_min = self._calculate_q_min_middle
        self.dqx_min = 0.0
        self.dqy_min = 0.0
        self.q_max = 0.0
        self.dqx_max = 0.0
        self.dqy_max = 0.0
        # Parameters from the AllCarriage Class
        self.dq_geometric = 0.0
        self.dq_wavelength = 0.0
        self.dq_gravity = 0.0
        set_params(instance=self, params=params)

    def update_dq_values(self):
        self.dq_geometric = self.parent.parent.all_carriage.dq_geometric
        self.dq_wavelength = self.parent.parent.all_carriage.dq_wavelength
        self.dq_gravity = self.parent.parent.all_carriage.dq_gravity

    def _calculate_dq(self, q=0.0, y_value=False):
        addition = math.pow(self.dq_gravity, 2) if y_value else 0.0
        return math.sqrt(math.pow(self.dq_geometric, 2) + math.pow(self.dq_wavelength * q, 2) + addition) / q

    def _calculate_q_min_middle(self):
        # The min values of Middle and front are different
        self.q_min = 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(
            self.parent.parent.all_carriage.two_theta_min / 2.0)

    def _calculate_q_min_front(self):
        self.q_min = min(abs(self.parent.left_panel.qx_min), abs(self.parent.left_panel.qx_max),
                         abs(self.parent.right_panel.qx_min), abs(self.parent.right_panel.qx_max))

    def _calculate_dQx_min(self):
        q = self.q_min
        self.dqx_min = self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_min(self):
        q = self.q_min
        self.dqy_min = self._calculate_dq(q=q, y_value=True)

    @staticmethod
    def _q_abs(qx, qy):
        return math.sqrt(math.pow(qx, 2) + math.pow(qy, 2))

    def calculate_qMax(self):
        self.q_max = max(self._q_abs(self.parent.left_panel.qx_min, self.parent.left_panel.qy_min),
                         self._q_abs(self.parent.left_panel.qx_max, self.parent.left_panel.qy_min),
                         self._q_abs(self.parent.left_panel.qx_min, self.parent.left_panel.qy_max),
                         self._q_abs(self.parent.left_panel.qx_max, self.parent.left_panel.qy_max),
                         self._q_abs(self.parent.right_panel.qx_min, self.parent.right_panel.qy_min),
                         self._q_abs(self.parent.right_panel.qx_max, self.parent.right_panel.qy_min),
                         self._q_abs(self.parent.right_panel.qx_min, self.parent.right_panel.qy_max),
                         self._q_abs(self.parent.right_panel.qx_max, self.parent.right_panel.qy_max))

    def _calculate_dQx_max(self):
        q = self.q_max
        self.dqx_max = self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_max(self):
        q = self.q_max
        self.dqy_max = self._calculate_dq(q=q, y_value=True)

    def calculate_d_q_values(self):
        self._calculate_dQx_min()
        self._calculate_dQy_min()
        self._calculate_dQx_max()
        self._calculate_dQy_max()

    def calculate_all_dq(self):
        if self.parent.name == "front_carriage":
            self.calculate_q_min = self._calculate_q_min_front
        self.update_dq_values()
        self.calculate_q_min()
        self.calculate_qMax()
        self.calculate_d_q_values()


class VerticalPanel:
    """Left and right panels

    """

    def __init__(self, parent, params, name="VerticalPanel", short_name="MR"):
        self.parent = parent
        self.name = name
        self.short_name = short_name
        self.horizontal_orientation = False
        self.lateral_offset = 0.0
        self.qx_min = 0.0  # Left
        self.qx_max = 0.0  # Right
        self.qy_min = 0.0  # Bottom
        self.qy_max = 0.0  # Top
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0
        self.is_valid = 0.0
        self.match_button = None
        self.detectors = Detector(where=short_name)

        # Constants needed for plotting
        self.x_pixel_size = 0.84
        self.y_pixel_size = 0.8
        self.pixel_num_x = 48.0
        self.pixel_num_y = 128.0
        self.beam_center_x = 0.0
        self.beam_center_y = 0.0
        self.beam_center_x_pix = 0.0
        self.beam_center_y_pix = 0.0

        # Detector Arrays
        self.data = []
        self.detector_array = []
        self.q_to_t_array = []
        self.qx_array = []
        self.qy_array = []
        self.qz_array = []
        self.default_mask = []
        self.data_real_dist_x = []  # data_realDistX
        self.data_real_dist_y = []  # data_realDistY

        set_params(instance=self, params=params)

    def calculate_match(self):
        if self.match_button is not None:
            if self.match_button:
                if self.short_name.find("L") != -1:
                    self._calculate_match_left()
                else:
                    self._calculate_match_right()
                self.parent.parent.options[self.name + "+lateral_offset"] = {"type": "readonly", "set_to": True}
            else:
                self.parent.parent.options[self.name + "+lateral_offset"] = {"type": "readonly", "set_to": False}

    def _calculate_match_left(self):
        middle_object = self.parent.parent.middle_carriage
        xmin = middle_object.left_panel.detectors.x_min(
            middle_object.left_panel.lateral_offset) - middle_object.refBeamCtr_x
        angle_min = math.atan2(xmin, middle_object.ssd)
        fr_xmax = math.tan(angle_min) * self.parent.ssd + self.refBeamCtr_x
        self.lateral_offset = self.detectors.lateral_offset_from_x_max(fr_xmax)

    def _calculate_match_right(self):
        middle_object = self.parent.parent.middle_carriage
        xmax = middle_object.right_panel.detectors.x_max(
            middle_object.right_panel.lateral_offset) - middle_object.refBeamCtr_x
        angle_max = math.atan2(xmax, middle_object.ssd)
        fr_xmin = math.tan(angle_max) * self.parent.ssd + self.refBeamCtr_x
        self.lateral_offset = self.detectors.lateral_offset_from_x_min(fr_xmin)

    def _calculate_q_helper(self, value):
        return 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(math.atan2(value, self.parent.ssd) / 2)

    def calculate_qx_min(self):
        xmin = self.detectors.x_min(self.lateral_offset) - self.refBeamCtr_x
        self.qx_min = self._calculate_q_helper(value=xmin)

    def calculate_qx_max(self):
        xmax = self.detectors.x_max(self.lateral_offset) - self.refBeamCtr_x
        self.qx_max = self._calculate_q_helper(value=xmax)

    def calculate_qy_min(self):
        ymin = self.detectors.y_min() - self.refBeamCtr_y
        self.qy_min = self._calculate_q_helper(value=ymin)

    def calculate_qy_max(self):
        ymax = self.detectors.y_max() - self.refBeamCtr_y
        self.qy_max = self._calculate_q_helper(value=ymax)

    def create_detector_array(self):
        """Creates 5 arrays of zeros based on the number of x and y pixels

        :return: Nothing as it just sets the value of detector_array, q_to_t_array, qx_array, qy_array, and qz_array
        :rtype: None
        """
        self.detector_array = np.zeros((int(self.pixel_num_x), int(self.pixel_num_y)))
        self.q_to_t_array = np.copy(self.detector_array)
        self.qx_array = np.copy(self.detector_array)
        self.qy_array = np.copy(self.detector_array)
        self.qz_array = np.copy(self.detector_array)
        self.data_real_dist_x = np.copy(self.detector_array)
        self.data_real_dist_y = np.copy(self.detector_array)
        self.data = np.copy(self.detector_array)

    def create_default_mask(self):
        if 'L' in self.short_name:
            inner_array = np.concatenate((np.ones(5), np.zeros(118), np.ones(5)))
            self.default_mask = np.concatenate((np.zeros((4, 128)), np.tile(inner_array, (44, 1))))
        else:
            inner_array = np.concatenate((np.ones(5), np.zeros(118), np.ones(5)))
            self.default_mask = np.concatenate((np.tile(inner_array, (44, 1)), np.zeros((4, 128))))

    def create_tmp_array(self):
        tmp_calib = np.zeros((3, 48))
        for a in range(48):
            tmp_calib[0][a] = -512
            tmp_calib[1][a] = 8
            tmp_calib[2][a] = 0
        return tmp_calib

    def calculate_panel(self):
        # Update values to be used
        self.refBeamCtr_x = self.parent.refBeamCtr_x
        self.refBeamCtr_y = self.parent.refBeamCtr_y
        self.calculate_match()  # This needs to run first as it affects the values for the rest of the calculations
        self.calculate_qx_min()
        self.calculate_qx_max()
        self.calculate_qy_min()
        self.calculate_qy_max()


class HorizontalPanel:
    """Top and bottom panels
    """

    def __init__(self, parent, params, name="HorizontalPanel", short_name="FT"):
        self.parent = parent
        self.name = name
        self.short_name = short_name
        self.horizontal_orientation = True
        self.verticalOffset = 0.0
        self.qy_min = 0.0  # Bottom
        self.qy_max = 0.0  # Top
        self.refBeamCtr_y = 0.0
        self.is_valid = 0.0
        self.match_button = False
        self.detectors = Detector(where=short_name)

        # Constants needed for plotting
        self.x_pixel_size = 0.4
        self.y_pixel_size = 0.84
        self.pixel_num_x = 128.0
        self.pixel_num_y = 48.0
        self.beam_center_x = 0.0
        self.beam_center_y = 0.0
        self.setback = 41  # CM

        # Detector Arrays
        self.data = []  # Data though through a differnt path
        self.detector_array = []  # det_FL
        self.q_to_t_array = []  # qTot_FL
        self.qx_array = []  # qTot_FL
        self.qy_array = []  # qx_FL
        self.qz_array = []  # qy_FL
        self.default_mask = []  # qz_FL
        self.data_real_dist_x = []  # data_realDistX
        self.data_real_dist_y = []  # data_realDistY

        set_params(instance=self, params=params)

    def calculate_match(self):
        if self.match_button is not None:
            if self.match_button:
                if self.short_name.find("T") != -1:
                    self._calculate_match_top()
                else:
                    self._calculate_match_bottom()
                self.parent.parent.options[self.name + "+verticalOffset"] = {"type": "readonly", "set_to": True}
            else:
                self.parent.parent.options[self.name + "+verticalOffset"] = {"type": "readonly", "set_to": False}

    def _calculate_match_bottom(self):
        middle_object = self.parent.parent.middle_carriage
        ymin = middle_object.right_panel.detectors.y_min(0) - middle_object.refBeamCtr_y
        angle_min = math.atan2(ymin, middle_object.ssd)
        fr_ymax = math.tan(angle_min) * (self.parent.ssd + self.detectors.setback) + self.refBeamCtr_y
        self.verticalOffset = self.detectors.vertical_offset_from_y_max(fr_ymax)

    def _calculate_match_top(self):
        middle_object = self.parent.parent.middle_carriage
        ymax = middle_object.right_panel.detectors.y_max(0) - middle_object.refBeamCtr_y
        angle_max = math.atan2(ymax, middle_object.ssd)
        fr_ymin = math.tan(angle_max) * (self.parent.ssd + self.detectors.setback) + self.refBeamCtr_y
        self.verticalOffset = self.detectors.vertical_offset_from_y_min(fr_ymin)

    def _calculate_q_helper(self, value):
        return 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(
            math.atan2(value, self.parent.ssd + self.detectors.setback) / 2)

    def calculate_qy_min(self):
        # var ymin = detectors.detector_FT.y_min(this.top_front_offset) - this.front_reference_yctr;;
        # return 4 * Math.PI / this.lambda *Math.sin(Math.atan2(ymin, this.SDD_front + detectors.detector_FT.setback) / 2);
        ymin = self.detectors.y_min(self.verticalOffset) - self.refBeamCtr_y
        self.qy_min = self._calculate_q_helper(value=ymin)

    def calculate_qy_max(self):
        # var ymax = detectors.detector_FB.y_max(this.bottom_front_offset) - this.front_reference_yctr;
        # return 4 * Math.PI / this.lambda *Math.sin(Math.atan2(ymax, this.SDD_front + detectors.detector_FB.setback) / 2)
        ymax = self.detectors.y_max(self.verticalOffset) - self.refBeamCtr_y
        self.qy_max = self._calculate_q_helper(value=ymax)

    def create_detector_array(self):
        """Creates 5 arrays of zeros based on the number of x and y pixels

        :return: Nothing as it just sets the value of detector_array, q_to_t_array, qx_array, qy_array, and qz_array
        :rtype: None
        """
        self.detector_array = np.zeros((int(self.pixel_num_x), int(self.pixel_num_y)))
        self.q_to_t_array = np.copy(self.detector_array)
        self.qx_array = np.copy(self.detector_array)
        self.qy_array = np.copy(self.detector_array)
        self.qz_array = np.copy(self.detector_array)
        self.data_real_dist_x = np.copy(self.detector_array)
        self.data_real_dist_y = np.copy(self.detector_array)
        self.data = np.copy(self.detector_array)

    def create_default_mask(self):
        self.default_mask = np.concatenate((np.ones((50, 48)), np.zeros((28, 48)), np.ones((50, 48))))

    def create_tmp_array(self):
        tmp_calib = np.zeros((3, 48))
        for a in range(48):
            tmp_calib[0][a] = -256
            tmp_calib[1][a] = 4
            tmp_calib[2][a] = 0
        return tmp_calib

    def calculate_panel(self):
        # Update values to be used
        self.refBeamCtr_y = self.parent.refBeamCtr_y
        self.calculate_match()  # This needs to run first as it affects the values for the rest of the calculations
        self.calculate_qy_min()
        self.calculate_qy_max()


class Detector:
    """ A class for the detector constants needed for calculations
    """

    def __init__(self, where="MR"):
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
        # If statements based off the name of the detector
        v_spatial_calibration = [-52.1, 0.814, 0]  # CM
        h_spatial_calibration = [-26.6, 0.416, 0]
        if self.name == "ML":
            self.id = "detector_ML"
            self.spatial_calibration = v_spatial_calibration
            self.setback = 0
            self.x_ctr_offset = 0.26
            self.y_ctr_offset = -0.16
            self.orientation = "VERTICAL"
            self.left_or_bottom = True
            self.panel_gap = 0.59

        elif self.name == "MT":
            self.id = "detector_MT"
            self.spatial_calibration = h_spatial_calibration
            self.setback = 41
            self.x_ctr_offset = -0.28
            self.y_ctr_offset = 0.6
            self.orientation = "HORIZONTAL"
            self.left_or_bottom = False
            self.panel_gap = 1.83

        elif self.name == "MB":
            self.id = "detector_MB"
            self.spatial_calibration = h_spatial_calibration
            self.setback = 41
            self.x_ctr_offset = -0.89
            self.y_ctr_offset = 0.96
            self.orientation = "HORIZONTAL"
            self.left_or_bottom = True
            self.panel_gap = 1.83

        elif self.name == "FR":
            self.id = "detector_FR"
            self.spatial_calibration = v_spatial_calibration
            self.setback = 0
            self.x_ctr_offset = 0
            self.y_ctr_offset = 0
            self.orientation = "VERTICAL"
            self.left_or_bottom = False
            self.panel_gap = 0.35

        elif self.name == "FL":
            self.id = "detector_FL"
            self.spatial_calibration = v_spatial_calibration
            self.setback = 0
            self.x_ctr_offset = 0.13
            self.y_ctr_offset = 0.35
            self.orientation = "VERTICAL"
            self.left_or_bottom = True
            self.panel_gap = 0.35

        elif self.name == "FT":
            self.id = "detector_FT"
            self.spatial_calibration = h_spatial_calibration
            self.setback = 41
            self.x_ctr_offset = 1.59
            self.y_ctr_offset = 0.09
            self.orientation = "HORIZONTAL"
            self.left_or_bottom = False
            self.panel_gap = 0.33

        elif self.name == "FB":
            self.id = "detector_FB"
            self.spatial_calibration = h_spatial_calibration
            self.setback = 41
            self.x_ctr_offset = 0.95
            self.y_ctr_offset = 0.77
            self.orientation = "HORIZONTAL"
            self.left_or_bottom = True
            self.panel_gap = 0.33
        else:
            self.id = "detector_MR"
            self.spatial_calibration = v_spatial_calibration
            self.setback = 0
            self.x_ctr_offset = 0
            self.y_ctr_offset = 0
            self.orientation = "VERTICAL"
            self.left_or_bottom = False
            self.panel_gap = 0.59

    def update_params(self):
        # Fix the value of this as there are issues with this value

        self._coord1_zero_pos = -(self.panel_gap / 2.0 + (
                self.num_tubes * self.tube_width)) if self.left_or_bottom else self.panel_gap / 2.0
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
        # convert pixel to spatial dimension, along tube length;
        return self.spatial_calibration[0] - self._coord0_ctr_offset + self.spatial_calibration[1] * pixel + \
            self.spatial_calibration[2] * math.pow(pixel, 2)

    def _pixel_to_coord1(self, pixel):
        return (pixel + 0.5) * self.tube_width + self._coord1_zero_pos - self._coord1_ctr_offset

    def _coord0_to_pixel(self, coord0):
        beta = math.sqrt(self.spatial_calibration[2])
        if beta == 0:
            return (coord0 - self.spatial_calibration[0] + self._coord0_ctr_offset) / self.spatial_calibration[1]
        else:
            alpha = self.spatial_calibration[1] / (2 * beta)
            # pick the right sign?
            return (alpha + math.sqrt(coord0 - self.spatial_calibration[0] + self._coord0_ctr_offset + alpha)) / beta

    def _coord1_to_pixel(self, coord1):
        return (coord1 - self._coord1_zero_pos + self._coord0_ctr_offset) / self.tube_width - 0.5

    def x_min(self, lateral_offset):
        return self.x(0) + (lateral_offset or 0)

    def x_max(self, lateral_offset):
        return self.x(self.x_dim - 1) + (lateral_offset or 0)

    def y_min(self, vertical_offset=None):
        return self.y(0) + (vertical_offset or 0)

    def y_max(self, vertical_offset=None):
        return self.y(self.y_dim - 1) + (vertical_offset or 0)

    def lateral_offset_from_x_max(self, x):
        return x - self.x_max(0)

    def lateral_offset_from_x_min(self, x):
        return x - self.x_min(0)

    def vertical_offset_from_y_max(self, y):
        return y - self.y_max(0)

    def vertical_offset_from_y_min(self, y):
        return y - self.y_min(0)
