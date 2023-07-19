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
        self.frontend_trans_options = []
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
        self.numGuides = 0  # No calculation necessary just get the value
        self.sourceAperture_js = 0.0  # The one coming from the js
        self.sourceAperture = 0.0  # The one that is used for the calculations
        self.sourceDistance = 0.0
        self.t_filter = 0.0
        self.t_guide = 0.0
        self.sample_aperture = 0.0
        self.extSampleAperture = 0.0 # This is a constant and does not need to be calculated
        self.sampleToApGv = 0.0
        self.sampleToGv = 0.0
        self.l_1 = 0.0
        self.aOverL = 0.0

        set_params(instance=self, params=params)

    def calculate_source_aperture(self):
        # return parseFloat(this.source_aperture_str) / 10.0
        self.sourceAperture = float(self.sourceAperture_js) / 10.0

    def calculate_t_filter(self):
        # Calculation run in beam.calculate_beam_current()
        lambda_val = self.parent.beam.wavelength
        self.t_filter = math.exp(-0.371 - 0.0305 * lambda_val - 0.00352 * math.pow(lambda_val, 2))

    def calculate_sample_aperture(self):
        self.sample_aperture = self.extSampleAperture / 10.0

    def calculate_collimation(self):
        pass


class MiddleCarriage:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name

        # Create the secondary object off the main object
        self.leftPanel = MidLeftPanel(self, params.get("MidLeftPanel", {}))
        self.rightPanel = MidRightPanel(self, params.get("MidRightPanel", {}))

        # Creates all the necessary parameters for the middle carriage class
        self.ssdInput = 0.0
        self.ssd = 0.0
        self.L_2 = 0.0
        self.beamDrop = 0.0
        self.beamstopRequired = 0.0
        self.Beamstop = 0.0
        self.θ2_min = 0.0
        self.q_min = 0.0
        self.dQx_Middle_min = 0.0
        self.dQy_Middle_min = 0.0
        self.qMax = 0.0
        self.dQx_Middle_max = 0.0
        self.dQy_Middle_max = 0.0
        self.refBeamCtr_x = 0.0
        self.refBeamCtr_y = 0.0

        params = params.get("MiddleCarriage", {})

        set_params(instance=self, params=params)

    def calculate_middleCarriage(self):
        self.leftPanel.calculate_midLeftPanel()
        self.rightPanel.calculate_midRightPanel()


class MidLeftPanel:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.lateralOffset = 0.0
        self.Q_right = 0.0
        self.qx_ML_min = 0.0

        set_params(instance=self, params=params)

    def calculate_midLeftPanel(self):
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
