from .instrument import set_params
import math


class Beam:
    def __init__(self, parent, params, name=None):
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
        self.frontend_trans = self.frontend_trans_options[str(self.dlambda)]

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
    def __init__(self, parent, params, name=None):
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
        return self.sourceDistance - self.sampleToApGv

    def calculate_aOverL(self):
        return math.pow((math.pi / 4.0 * self.sourceAperture * self.sample_aperture / self.l_1), 2)

    def calculate_collimation(self):
        self.calculate_num_guides()
        self.calculate_source_aperture()
        self.calculate_sourceDistance()
        self.calculate_t_guide()
        self.calculate_sample_aperture()
        self.calculate_l_1()
        self.calculate_aOverL()


class DqCalculator:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name

        self.q_min = 0.0
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

    def calculate_d_q_values(self):
        self._calculate_dQx_min()
        self._calculate_dQy_min()  # self._calculate_dQx_max()  # self._calculate_dQy_max()

    # Not sure why I have this
    def _calculate_dq(self, q=0.0, y_value=False):
        addition = math.pow(self.dq_gravity, 2) if y_value else 0.0
        return math.sqrt(math.pow(self.dQ_geometric, 2) + math.pow(self.dq_wavelength * q, 2) + addition) / q

    def calculate_q_min(self):
        self.q_min = 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(
            self.parent.parent.all_carriage.θ2_min / 2.0)

    def _calculate_dQx_min(self):
        q = self.q_min
        self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_min(self):
        q = self.q_min
        self._calculate_dq(q=q, y_value=True)

    def calculate_qMax(self):
        pass

    def _calculate_dQx_max(self):
        q = self.qMax
        self._calculate_dq(q=q, y_value=False)

    def _calculate_dQy_max(self):
        q = self.qMax
        self._calculate_dq(q=q, y_value=True)

    def calculate_all_dq(self):
        self.update_dq_values()
        self.calculate_q_min()
        self.calculate_qMax()
        self.calculate_d_q_values()


class AllCarriage:
    def __init__(self, parent, params, name=None):
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
        self.beamstopRequired = beam_size_geometric + gravity_width

    def calculate_θ2_min(self):
        # Also known as TwoTheta_min
        #        return Math.atan2(this.beamstop / 2, this.SDD_middle);
        self.parent.middle_Carriage.calculate_ssd()
        self.θ2_min = math.atan2(self.Beamstop / 2, self.parent.middle_Carriage.ssd)

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
        self.calculate_θ2_min()
        # Runs more calculation statements
        self.calculate_overall_d_q_values()


class MiddleCarriage:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name

        # Create the secondary object off the main object
        self.leftPanel = Panel(self, params.get("MidLeftPanel", {}))
        self.rightPanel = MidRightPanel(self, params.get("MidRightPanel", {}))
        self.dqCalc = DqCalculator(self, params.get("DqCalc"), {})

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

    def calculate_refBeamCtr_x(self):
        pass

    def calculate_refBeamCtr_y(self):
        pass

    def calculate_middleCarriage(self):
        # Calculates all the parameters of this object
        self.calculate_ssd()
        self.calculate_refBeamCtr_x()
        self.calculate_refBeamCtr_y()
        # Calculates the 2 other panels
        self.leftPanel.calculate_panel()
        self.rightPanel.calculate_midRightPanel()
        self.dqCalc.calculate_all_dq()


class Panel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.Q_right = 0.0
        self.qx_ML_min = 0.0

        set_params(instance=self, params=params)

    def calculate_panel(self):
        pass


class MidRightPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.qx_MR_min = 0.0
        self.qx_MR_max = 0.0
        self.qy_MR_min = 0.0
        self.qy_MR_max = 0.0

        set_params(instance=self, params=params)

    def calculate_midRightPanel(self):
        pass


class FrontCarriage:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        # Create the secondary object off the main object
        self.leftPanel = FrontLeftPanel(self, params.get("FrontLeftPanel", {}))
        self.rightPanel = FrontRightPanel(self, params.get("FrontRightPanel", {}))
        self.topPanel = FrontTopPanel(self, params.get("FrontTopPanel", {}))
        self.bottomPanel = FrontBottomPanel(self, params.get("FrontBottomPanel", {}))
        self.dqCalc = DqCalculator(self, params.get("DqCalc"), {})
        params = params.get("FrontCarriage", {})

        # Creates all the necessary parameters for the Front carriage class
        self.qmin = 0.0
        self.dQx_Front_min = 0.0
        self.dQy_Front_min = 0.0
        self.qMax = 0.0
        self.dQx_Front_max = 0.0
        self.dQy_Front_max = 0.0
        self.ssd_input = 0.0
        self.ssd = 0.0
        self.refBeamCtrX = 0.0
        self.RefBeamCtrY = 0.0

        set_params(instance=self, params=params)

    def calculate_frontCarriage(self):
        self.leftPanel.calculate_frontLeftPanel()
        self.rightPanel.calculate_frontRightPanel()
        self.topPanel.calculate_frontTopPanel()
        self.bottomPanel.calculate_frontBottomPanel()
        self.dqCalc.calculate_all_dq()


class FrontLeftPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.q_right = 0.0
        self.q_left = 0.0
        self.matchMLButton = 0.0
        set_params(instance=self, params=params)

    def calculate_frontLeftPanel(self):
        pass


class FrontRightPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.q_Left = 0.0
        self.q_Right = 0.0
        self.matchRightMR = 0.0

        set_params(instance=self, params=params)

    def calculate_frontRightPanel(self):
        pass


class FrontTopPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.verticalOffset = 0.0
        self.qBottom = 0.0
        self.q_Top = 0.0
        self.matchTopMR = 0.0

        set_params(instance=self, params=params)

    def calculate_frontTopPanel(self):
        pass


class FrontBottomPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.verticalOffset = 0.0
        self.q_Top = 0.0
        self.q_Bottom = 0.0
        self.matchBottomMR = 0.0

        set_params(instance=self, params=params)

    def calculate_frontBottomPanel(self):
        pass
