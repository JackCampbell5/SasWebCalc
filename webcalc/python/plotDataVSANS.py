from .instrument import set_params
import math


class PlotData:
    def __init__(self, parent, params, name="PlotData"):
        self.parent = parent
        self.name = name
        self.middle_carriage = None
        self.mid_left_panel = None
        self.mid_right_panel = None
        self.front_carriage = None
        self.front_left_panel = None
        self.front_right_panel = None
        self.front_top_panel = None
        self.front_bottom_panel = None
        set_params(instance=self, params=params)

    def recalculate_all_detectors(self):
        # calculates Q for each panel and fills 2D panels with model data then plots the 2D panel
        # self.plot_back_panel() # We are not worrying about the back Panel
        self.plot_middle_panel()
        self.plot_front_panel()

        # generate a proper mask based on hard + soft shadowing
        self.reset_mask()
        self.draw_mask()

        # update values on the panel
        self.calculate_beam_intensity()

        # Fill in the Qmin and Qmax values, based on Q_Tot for the 2D panels ( not including mask)
        # self.v_q_min_max_back() # We are not worrying about the back Panel
        self.v_q_min_max_middle()
        self.v_q_min_max_front()

        # Calculate beam diameter and beamstop size
        # V_BeamDiamDisplay("maximum", "MR") // TODO - - hard - wired here for the Middle carriage ( and in the
        #  SetVar label)
        # V_BeamStopDiamDisplay("MR")

        self.beam_biam_display()
        self.beam_stop_diam_display()
        # Calculate the "real" QMin with the beamstop
        # V_QMin_withBeamStop("MR") // TODO - - hard - wired
        #
        self.calculate_q_min_beam_stop()
        #
        # The 1 D I(q) - get the values, re - do the calc at the end
        # popStr
        # collimationStr = "pinhole"
        # ControlInfo / W = VCALC
        # popup_b
        # popStr = S_Value
        # V_QBinAllPanels_Circular("VCALC", V_BinTypeStr2Num(popStr), collimationStr)
        self.bin_all_panels_circular()
        #
        # Plot the results(1 D)
        # type = "VCALC"
        # String
        # str, winStr = "VCALC#Panels_IQ", workTypeStr
        # workTypeStr = "root:Packages:NIST:VSANS:" + type
        #
        # sprintf
        # str, "(\"%s\",%d,\"%s\")", workTypeStr, V_BinTypeStr2Num(popStr), winStr
        # Execute("V_Back_IQ_Graph" + str)
        #
        # Execute("V_Middle_IQ_Graph" + str)
        #
        # Execute("V_Front_IQ_Graph" + str)
        #
        # Multiply the averaged data by the shadow factor to simulate a beamstop
        self.iq_beam_stop_shadow()

    def plot_middle_panel(self):
        # fPlotMiddlePanels in IgorPro
        # calculate Qtot, qxqyqz arrays from geometry
        self.calculate_q_middle_panels()

    def calculate_q_middle_panels(self):
        # VC_CalculateQMiddlePanels in IgorPro
        M_L_sep = self.get_panel_translation("ML")
        M_R_sep = self.get_panel_translation("MR")
        M_T_sep = self.get_panel_translation("MT")
        M_B_sep = self.get_panel_translation("MB")

    def get_panel_translation(self, type):
        # VCALC_getPanelTranslation in IgorPro
        if type == "FL":
            #Left offset value?
            pass
        return 0

    def plot_front_panel(self):
        pass

    def reset_mask(self):
        pass

    def draw_mask(self):
        pass

    def calculate_beam_intensity(self):
        pass

    def v_q_min_max_middle(self):
        pass

    def v_q_min_max_front(self):
        pass

    def beam_biam_display(self):
        pass

    def beam_stop_diam_display(self):
        pass

    def calculate_q_min_beam_stop(self):
        pass

    def bin_all_panels_circular(self):
        pass

    def iq_beam_stop_shadow(self):
        pass
