from .instrument import set_params


class Beam:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.wavelength = 0
        self.dlambda = 0.0
        self.frontendTrans = 0.0
        self.flux = 0.0
        self.beamCurrent = 0.0
        self.iSub0 = 0.0
        self.frontend_trans_options = []
        self.name = name
        set_params(instance=self, params=params)

    def calculate_frontend_trans(self):
        print(self.dlambda)
        self.frontend_trans = self.frontend_trans_options[str(self.dlambda)]
        print(self.frontend_trans)

    def calculate_beam(self):
        self.calculate_frontend_trans()


class Collimation:
    def __init__(self, parent, params, name=None):
        self.parent = parent
        self.name = name
        self.numGuides = 0.0
        self.sourceAperture = 0.0
        self.sourceDistance = 0.0
        self.t_filter = 0.0
        self.t_guide = 0.0
        self.extSampleAperture = 0.0
        self.sampleToApGv = 0.0
        self.sampleToGv = 0.0
        self.l_1 = 0.0
        self.aOverL = 0.0

        set_params(instance=self, params=params)

    def calculate_collimation(self):
        pass


class MiddleCarriage:
    def __init__(self, parent, params, name=None):

        self.parent = parent
        self.name = name

        # Create the secondary object off the main object
        self.leftPanel = MidLeftPanel(self, params.get("MidLeftPanel", {}))
        self.rightPanel = MidRightPanel(self, params.get("MidRightPanel", {}))

        #Creates all the necessary parameters for the middle carriage class
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

        #Creates all the necessary parameters for the Front carriage class
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
