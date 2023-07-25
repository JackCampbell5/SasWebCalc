from .instrument import set_params
import math


class Beam:
    def __init__(self, parent, params, name="Beam"):
        self.parent = parent
        self.wavelength = 0  # Known as lamda in the js
        self.dlambda = 0.0
        self.lambda_T = 0.0
        self.phi_0 = 0.0
        self.frontendTrans = 0.0
        self.flux = 0.0
        self.beamCurrent = 0.0
        self.iSub0 = 0.0  # or Incident_Intensity
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
        self.frontendTrans = self.frontend_trans_options[str(self.dlambda)]

    def calculate_flux(self):
        lfrac = self.lambda_T / self.wavelength
        self.flux = (self.dlambda * math.pow(lfrac, 4) * math.exp(-math.pow(lfrac, 2)) * self.phi_0) / 2.0 * math.pi

    def calculate_beam_current(self):
        self.parent.collimation.calculate_t_filter()
        t_filter = self.parent.collimation.t_filter
        self.beamCurrent = self.frontendTrans * t_filter

    def calculate_iSub0(self):
        collimation = self.parent.collimation
        collimation.calculate_sample_aperture()
        self.iSub0 = self.beamCurrent / (math.pi * math.pow(collimation.sample_aperture / 2.0, 2))

    def calculate_beam(self):
        self.calculate_wavelength()
        self.calculate_frontend_trans()
        self.calculate_flux()
        self.calculate_beam_current()
        self.calculate_iSub0()


class Collimation:
    def __init__(self, parent, params, name="Collimation"):
        self.parent = parent
        self.name = name
        self.guide_select = 0
        self.numGuides = 0  # No calculation necessary just get the value
        self.cov_beams = False
        self.sourceAperture_js = 0.0  # The one coming from the js ( No Calculation Necessary)
        self.sourceAperture = 0.0  # The one that is used for the calculations
        self.sourceDistance = 0.0
        self.sourceDistance_options = [2441, 2157, 1976, 1782, 1582, 1381, 1181, 980, 780, 579]
        self.t_filter = 0.0
        self.t_guide = 0.0
        self.sample_aperture = 0.0
        self.extSampleAperture = 0.0  # This is a constant and does not need to be calculated
        self.sampleToApGv = 0.0
        self.sampleToGv = 0.0
        self.l_1 = 0.0
        self.aOverL = 0.0

        set_params(instance=self, params=params)

    def calculate_num_guides(self):
        self.numGuides = 0 if self.guide_select == "CONV_BEAMS" or self.guide_select == "NARROW_SLITS" else int(
            self.guide_select)

    def calculate_source_aperture(self):
        """Calculates the value of the source aperture

        :return: None as it just sets a value
        """
        self.sourceAperture = float(self.sourceAperture_js) / 10.0

    def calculate_sourceDistance(self):
        self.sourceDistance = self.sourceDistance_options[self.numGuides]

    def calculate_t_filter(self):
        # Calculation run in beam.calculate_beam_current()
        lambda_val = self.parent.get_wavelength()
        self.t_filter = math.exp(-0.371 - 0.0305 * lambda_val - 0.00352 * math.pow(lambda_val, 2))

    def calculate_t_guide(self):
        return math.pow(0.97, self.numGuides)

    def calculate_sample_aperture(self):
        self.sample_aperture = self.extSampleAperture / 10.0

    def calculate_l_1(self):
        self.l_1 = self.sourceDistance - self.sampleToApGv

    def calculate_aOverL(self):
        self.aOverL = math.pow((math.pi / 4.0 * self.sourceAperture * self.sample_aperture / self.l_1), 2)

    def calculate_collimation(self):
        self.calculate_num_guides()
        self.calculate_source_aperture()
        self.calculate_sourceDistance()
        self.calculate_t_guide()
        self.calculate_sample_aperture()
        self.calculate_l_1()
        self.calculate_aOverL()


class AllCarriage:
    def __init__(self, parent, params, name="AllCarriage"):
        self.parent = parent
        self.name = name

        # In Middle Carriage in the JS
        self.L_2 = 0.0
        self.imported_l_1 = 0.0
        self.beamDrop = 0.0  # Also know as Gravity_Drop_Mean in the JS
        self.gravity_Drop_Min = 0.0
        self.gravity_Drop_Max = 0.0
        self.beamstopRequired = 0.0
        self.Beamstop = 0.0
        self.beamStopCm = 0.0
        self.θ2_min = 0.0
        # Values needed for the DQ calculations
        self.overall_dq_calculated = False
        self.dQ_geometric = 0.0
        self.dq_wavelength = 0.0
        self.dq_gravity = 0.0
        set_params(instance=self, params=params)

    def calculate_L_2(self):
        self.L_2 = self.parent.middle_Carriage.ssdInput + self.parent.collimation.sampleToApGv

    def calculate_beamDrop(self):
        # Also known as Gravity_Drop_Mean in the JS
        lambda_val = self.parent.get_wavelength()
        self.beamDrop = self._calculate_Gravity_Drop(lambda_val=lambda_val)

    def _calculate_Gravity_Drop(self, lambda_val=0.0):
        h_over_mn = 395603.0  # Angstrom cm / s
        g = 981.0  # cm/s^2
        return g / 2.0 * math.pow((lambda_val / h_over_mn), 2) * (
                math.pow((self.imported_l_1 + self.L_2), 2) - (self.imported_l_1 + self.L_2) * self.imported_l_1)

    def calculate_Gravity_Drop_Min(self):
        #         var lambda = this.lambda * (1.0 + this.dlambda);
        lambda_val = self.parent.get_wavelength() * (1.0 + self.parent.beam.dlambda)
        self.gravity_Drop_Min = self._calculate_Gravity_Drop(lambda_val=lambda_val)

    def calculate_Gravity_Drop_Max(self):
        lambda_val = self.parent.get_wavelength() * (1.0 - self.parent.beam.dlambda)
        self.gravity_Drop_Max = self._calculate_Gravity_Drop(lambda_val=lambda_val)

    def calculate_beamstopRequired(self):
        # Calculate the gravity drops needed for this problem
        self.calculate_Gravity_Drop_Min()
        self.calculate_Gravity_Drop_Max()
        # The actual calculations being done
        beam_size_geometric = self.parent.get_sourceAperture() * self.L_2 / self.imported_l_1 + self.parent.get_sample_aperture() * (
                self.imported_l_1 + self.L_2) / self.imported_l_1
        gravity_width = abs(self.gravity_Drop_Max - self.gravity_Drop_Min)
        beamstopRequired = beam_size_geometric + gravity_width
        # UNITS to get into CM
        self.beamstopRequired = beamstopRequired / 2.54

    def calculate_beam_stop_cm(self):
        self.beamStopCm = self.Beamstop * 2.54

    def calculate_θ2_min(self):
        # Also known as TwoTheta_min
        self.parent.middle_Carriage.calculate_ssd()
        self.θ2_min = math.atan2(self.beamStopCm / 2, self.parent.middle_Carriage.ssd)

    def calculate_overall_d_q_values(self):
        self._calculate_dQ_geometric()
        self._calculate_dq_wavelength()
        self._calculate_dq_gravity()
        self.overall_dq_calculated = True

    def _calculate_dQ_geometric(self):
        pixel_size = 0.82  # cm
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow((self.parent.get_l_2() * self.parent.get_sourceAperture()) / (4 * self.parent.get_l_1()), 2)
        c = math.pow((self.parent.get_l_1() + self.parent.get_l_2()) * self.parent.get_sample_aperture() / (
                4 * self.parent.get_l_1()), 2)
        d = math.pow(pixel_size / 2, 2) / 3
        self.dQ_geometric = a * math.sqrt(b + c + d)

    def _calculate_dq_wavelength(self):
        resolution_factor = 6.0
        self.dq_wavelength = self.parent.beam.dlambda / math.sqrt(resolution_factor)

    def _calculate_dq_gravity(self):
        g = 981.0  # CM/s^2
        h_over_mn = 395603.0  # Angstrom cm/s
        a = 2 * math.pi / (self.parent.get_wavelength() * self.parent.get_l_2())
        b = math.pow(g, 2) / (2 * math.pow(h_over_mn, 4))
        c = math.pow(self.L_2, 2) * math.pow(self.parent.get_l_1() + self.L_2, 2)
        d = math.pow(self.parent.get_wavelength(), 4) * 2 / 3 * math.pow(self.parent.beam.dlambda, 2)
        self.dq_gravity = a * math.sqrt(b * c * d)

    def calculate_All_Carriage(self):
        self.imported_l_1 = self.parent.get_l_1()
        self.calculate_L_2()
        self.calculate_beamDrop()
        self.calculate_beamstopRequired()  # Also Calls the gravity drop ones too
        self.calculate_beam_stop_cm()
        self.calculate_θ2_min()
        # Runs more calculation statements
        self.calculate_overall_d_q_values()


class MiddleCarriage:
    def __init__(self, parent, params, name="MiddleCarriage"):
        self.parent = parent
        self.name = name

        # Create the secondary object off the main object
        self.leftPanel = HorizontalPanel(self, params.get("MidLeftPanel", {}), name="ML")
        self.rightPanel = HorizontalPanel(self, params.get("MidRightPanel", {}), name="MR")
        self.dqCalc = DqCalculator(self, params.get("MidDqValues", {}))

        params = params.get("MiddleCarriage", {})

        # Creates all the necessary parameters for the middle carriage class
        self.ssdInput = 0.0  # This is just the value input by the user, not the actual SSD value
        self.ssd = 0.0
        # DQ Values that are used for both classes
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0
        set_params(instance=self, params=params)

    def calculate_ssd(self):
        self.ssd = self.ssdInput + self.parent.collimation.sampleToGv

    # create a class for the chnaging dq values and the constant calculated values are kept in the front apature clas
    # sbut there is a paramater that will be set saying the calculations can be done in the dependet classes

    def calculate_middleCarriage(self):
        # Calculates all the parameters of this object
        self.calculate_ssd()
        # Calculates the 2 other panels
        self.leftPanel.calculate_panel()
        self.rightPanel.calculate_panel()
        self.dqCalc.calculate_all_dq()


class FrontCarriage:
    def __init__(self, parent, params, name="FrontCarriage"):
        self.parent = parent
        self.name = name
        # Create the secondary object off the main object
        self.leftPanel = HorizontalPanel(self, params.get("FrontLeftPanel", {}), name="FL")
        self.rightPanel = HorizontalPanel(self, params.get("FrontRightPanel", {}), name="FR")
        self.topPanel = VerticalPanel(self, params.get("FrontTopPanel", {}), name="FT")
        self.bottomPanel = VerticalPanel(self, params.get("FrontBottomPanel", {}), name="FB")
        self.dqCalc = DqCalculator(self, params.get("FrontDqValues", {}))
        params = params.get("FrontCarriage", {})

        # Creates all the necessary parameters for the Front carriage class
        self.ssd_input = 0.0
        self.ssd = 0.0
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0

        set_params(instance=self, params=params)

    def calculate_ssd(self):
        self.ssd = self.ssd_input + self.parent.collimation.sampleToGv

    def calculate_frontCarriage(self):
        self.calculate_ssd()

        # Calculate the other objects
        self.leftPanel.calculate_panel()
        self.rightPanel.calculate_panel()
        self.topPanel.calculate_panel()
        self.bottomPanel.calculate_panel()
        self.dqCalc.calculate_all_dq()


class DqCalculator:
    def __init__(self, parent, params, name="DqCalculator"):
        self.parent = parent
        self.name = name

        self.q_min = 0.0
        self.calculate_q_min = self._calculate_q_min_middle
        self.dQx_min = 0.0
        self.dQy_min = 0.0
        self.qMax = 0.0
        self.dQx_max = 0.0
        self.dQy_max = 0.0
        # Parameters from the AllCarriage Class
        self.dQ_geometric = 0.0
        self.dq_wavelength = 0.0
        self.dq_gravity = 0.0
        set_params(instance=self, params=params)

    def update_dq_values(self):
        self.dQ_geometric = self.parent.parent.all_carriage.dQ_geometric
        self.dq_wavelength = self.parent.parent.all_carriage.dq_wavelength
        self.dq_gravity = self.parent.parent.all_carriage.dq_gravity

    def _calculate_dq(self, q=0.0, y_value=False):
        addition = math.pow(self.dq_gravity, 2) if y_value else 0.0
        return math.sqrt(math.pow(self.dQ_geometric, 2) + math.pow(self.dq_wavelength * q, 2) + addition) / q

    def _calculate_q_min_middle(self):
        # The min values of Middle and front are different
        self.q_min = 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(
            self.parent.parent.all_carriage.θ2_min / 2.0)

    def _calculate_q_min_front(self):
        self.q_min = min(abs(self.parent.leftPanel.qx_min), abs(self.parent.leftPanel.qx_max),
                         abs(self.parent.rightPanel.qx_min), abs(self.parent.rightPanel.qx_max))

    def _calculate_dQx_min(self):
        q = self.q_min
        self.dQx_min = self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_min(self):
        q = self.q_min
        self.dQy_min = self._calculate_dq(q=q, y_value=True)

    @staticmethod
    def _q_abs(qx, qy):
        return math.sqrt(math.pow(qx, 2) + math.pow(qy, 2))

    def calculate_qMax(self):
        self.qMax = max(self._q_abs(self.parent.leftPanel.qx_min, self.parent.leftPanel.qy_min),
                        self._q_abs(self.parent.leftPanel.qx_max, self.parent.leftPanel.qy_min),
                        self._q_abs(self.parent.leftPanel.qx_min, self.parent.leftPanel.qy_max),
                        self._q_abs(self.parent.leftPanel.qx_max, self.parent.leftPanel.qy_max),
                        self._q_abs(self.parent.rightPanel.qx_min, self.parent.rightPanel.qy_min),
                        self._q_abs(self.parent.rightPanel.qx_max, self.parent.rightPanel.qy_min),
                        self._q_abs(self.parent.rightPanel.qx_min, self.parent.rightPanel.qy_max),
                        self._q_abs(self.parent.rightPanel.qx_max, self.parent.rightPanel.qy_max))

    def _calculate_dQx_max(self):
        q = self.qMax
        self.dQx_max = self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_max(self):
        q = self.qMax
        self.dQy_max = self._calculate_dq(q=q, y_value=True)

    def calculate_d_q_values(self):
        self._calculate_dQx_min()
        self._calculate_dQy_min()
        self._calculate_dQx_max()
        self._calculate_dQy_max()

    def calculate_all_dq(self):
        if self.parent.name == "FrontCarriage":
            self.calculate_q_min = self._calculate_q_min_front
        self.update_dq_values()
        self.calculate_q_min()
        self.calculate_qMax()
        self.calculate_d_q_values()


class HorizontalPanel:
    def __init__(self, parent, params, name="HorizontalPanel"):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.qx_min = 0.0  # Left
        self.qx_max = 0.0  # Right
        self.qy_min = 0.0  # Bottom
        self.qy_max = 0.0  # Top
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0
        self.is_valid = 0.0
        self.match_button = False
        self.detectors = Detector(where=name)
        set_params(instance=self, params=params)

    def _calculate_q_helper(self, value):
        return 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(math.atan2(value, self.parent.ssd) / 2)

    def calculate_qx_min(self):
        xmin = self.detectors.x_min(self.lateralOffset) - self.refBeamCtr_x
        self.qx_min = self._calculate_q_helper(value=xmin)

    def calculate_qx_max(self):
        xmax = self.detectors.x_max(self.lateralOffset) - self.refBeamCtr_x
        self.qx_max = self._calculate_q_helper(value=xmax)

    def calculate_qy_min(self):
        ymin = self.detectors.y_min() - self.refBeamCtr_y
        self.qy_min = self._calculate_q_helper(value=ymin)

    def calculate_qy_max(self):
        ymax = self.detectors.y_max() - self.refBeamCtr_y
        self.qy_max = self._calculate_q_helper(value=ymax)

    def calculate_is_valid(self):
        pass

    def calculate_panel(self):
        # Update values to be used
        self.refBeamCtr_x = self.parent.refBeamCtr_x
        self.refBeamCtr_y = self.parent.refBeamCtr_y
        self.calculate_qx_min()
        self.calculate_qx_max()
        self.calculate_qy_min()
        self.calculate_qy_max()
        self.calculate_is_valid()


class VerticalPanel:
    def __init__(self, parent, params, name="VerticalPanel"):
        self.parent = parent
        self.name = name
        self.verticalOffset = 0.0
        self.qy_min = 0.0  # Bottom
        self.qy_max = 0.0  # Top
        self.refBeamCtr_y = 0.0
        self.is_valid = 0.0
        self.match_button = False
        self.detectors = Detector(where=name)
        set_params(instance=self, params=params)

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

    def calculate_is_valid(self):
        pass

    def calculate_panel(self):
        # Update values to be used
        self.refBeamCtr_y = self.parent.refBeamCtr_y
        self.calculate_qy_min()
        self.calculate_qy_max()
        self.calculate_is_valid()


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
