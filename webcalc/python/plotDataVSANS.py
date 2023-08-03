import numpy as np

from .instrument import set_params
import math


class PlotData:
    def __init__(self, parent, params, name="PlotData"):
        self.parent = parent
        self.name = name
        self.middle_carriage = None
        self.mid_left_panel = None
        self.mid_right_panel = None
        self.mid_top_panel = None
        self.mid_bottom_panel = None
        self.front_carriage = None
        self.front_left_panel = None
        self.front_right_panel = None
        self.front_top_panel = None
        self.front_bottom_panel = None
        self.all_detectors = None

        # Not object params
        self.lambda_val = 0.0
        self.default_mask = None

        set_params(instance=self, params=params)

    def run_plot_data(self):
        # Initialize the space and all the variables
        self.initialize_space()

        # Open the panel
        # self.draw_panel() # not necessary right now might be used later to set parameters

        # Generates default mask
        self.generate_default_mask()

        # Some other update that starts with a preset

        # Calculates all the data
        self.calculate_all_detectors()

        # Updates the views
        self.update_views()

    def initialize_space(self):
        # All the other variables are set in their classes as they are constants

        # Creates a object that contains all the detector objects and can be lopped through
        self.all_detectors = [self.mid_left_panel, self.mid_right_panel, self.mid_top_panel, self.mid_bottom_panel,
                              self.front_left_panel, self.front_right_panel, self.front_top_panel,
                              self.front_bottom_panel]

        # Creates each detector in the subclass
        for panel in self.all_detectors:
            panel.create_detector_array()

    def generate_default_mask(self):
        # if it matters we are using the gHighResBinning value of 4 as that is what is used for VCALC

        # Overall Default Mask
        inner_array = np.concatenate((np.ones(39), np.zeros(1496), np.ones(121)))
        self.default_mask = np.concatenate(
            (np.zeros((191, 1656)), np.tile(inner_array, (478, 1)), np.zeros((11, 1656))))

        # Generate thde default mask for each indevidual detector
        for panel in self.all_detectors:
            panel.create_default_mask()

    def calculate_all_detectors(self):
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

    def update_views(self):
        pass

    # Helper functions for the sub functions of run_plot_data
    def plot_middle_panel(self):
        # fPlotMiddlePanels in IgorPro
        # calculate Qtot, qxqyqz arrays from geometry
        self.calculate_q_middle_panels()

    def calculate_q_middle_panels(self):
        # VC_CalculateQMiddlePanels in IgorPro
        m_l_sep = self.mid_left_panel.lateral_offset
        m_r_sep = self.mid_right_panel.lateral_offset
        m_t_sep = self.mid_top_panel.verticalOffset
        m_b_sep = self.mid_bottom_panel.verticalOffset

        lam = self.lambda_val
        ssd_setback = 0
        self.make_real_dist_x_y_waves(self.front_left_panel)

    def make_real_dist_x_y_waves(self, panel_object):
        # VC_MakeRealDistXYWaves in IGORPro
        # make the data_realDistX,Y Waves that are needed for the calculation of q
        tmp_array = panel_object.create_tmp_array()
        tube_width = 8.4
        # self.non_linear_correction(data,tmpCalib,tube_width,detStr,destPath)
        self.non_linear_correction(tmp_array=tmp_array, tube_width=tube_width, panel_object=panel_object)

    def non_linear_correction(self, tmp_array, tube_width, panel_object):
        # V_NonLinearCorrection in igor
        horizontal_orientation = panel_object.horizontal_orientation
        # FIXME Get panel gap code is returning a null value
        diamX = len(panel_object.detector_array)
        diamy = len(panel_object.detector_array[0])
        # Find te panel gap from the list of constants
        if 'F' in panel_object.short_name:
            if not horizontal_orientation:
                gap = 3.5
            else:
                gap = 3.3
        else:
            if not horizontal_orientation:
                gap = 5.9
            else:
                gap = 18.3
        if not horizontal_orientation:
            offset = self.get_offset(panel_object=panel_object)
            offset = offset * 10
            k_bctr_cm = True  # set to 1 to use beam center in cm. O to use pixels
            if k_bctr_cm:
                if 'L' in panel_object.short_name:
                    other_array = np.zeros(len(panel_object.data_real_dist_x[0]))
                    for a in range(len(other_array)):
                        other_array[a] = offset - (diamX - a - .5) * tube_width - gap / 2

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

    @staticmethod
    def get_offset(panel_object):
        # VCALC_getPanelTranslation in IGOR
        if panel_object.horizontal_orientation:
            return panel_object.verticalOffset
        else:
            return panel_object.lateral_offset
