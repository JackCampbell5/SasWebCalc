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
        self.k_bctr_cm = True  # set to 1 to use beam center in cm. O to use pixels

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
        self.plot_all_panels()

        # generate a proper mask based on hard + soft shadowing
        self.reset_mask()
        for panel in self.all_detectors:
            self.draw_mask(panel)

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
    # Start calculate panel function
    def plot_all_panels(self):
        # fPlotMiddlePanels in IgorPro
        # calculate Qtot, qxqyqz arrays from geometry
        for panel in self.all_detectors:
            self.plot_panel(panel)
            self.fill_panel_w_model_data(
                panel)  # Middle Panels AsQ()  # self.  # TODO self.panel_asq(  # self.middle_carriage) # This displays the panel and checks ot make sure everything is  #  right

    def fill_panel_w_model_data(self, panel_object):
        # FillPanel_wModelData in Igor
        detector_array = panel_object.detector_array
        q_to_t = panel_object.q_to_t_array
        tmp_intren = np.copy(detector_array)
        tmp_sig = np.copy(detector_array)
        prob_i = np.copy(detector_array)

        imon = 1e+11
        trans = 0.8
        thick = 0.1
        ssd = self.get_ssd(panel_object)
        # Get the setback value of each part
        ssd = ssd + self.get_setback(panel_object)
        pix_size_x = panel_object.x_pixel_size
        pix_size_y = panel_object.y_pixel_size
        add_emp_bgd = 0
        func_str = "Debye"  # This is the model used for calculation

        def debye(x):
            scale = 10
            rg = 300
            bkg = 0.0001
            qr2 = math.pow(x * rg, 2)
            pq = 2 * (math.exp(-(qr2)) - 1 + qr2) / math.pow(qr2, 2)
            pq = pq * scale
            return pq + bkg

        for a in range(len(tmp_intren)):
            for b in range(len(tmp_intren[0])):
                tmp_intren[a][b] = debye(panel_object.q_to_t_array[a][b])
        # Id not implement if add_emp_bgd ad it did not seem necessary without model application
        # I also did not implement if back detector as we do not have the back director at this time
        prob_i = trans * thick * pix_size_x * pix_size_y / math.pow(ssd, 2) * tmp_intren
        tmp_intren = (imon) * prob_i
        for a in range(len(tmp_intren)):
            for b in range(len(tmp_intren[a])):
                tmp_sig[a][b] = math.sqrt(tmp_intren[a][b])
        # TODO Implement gnoise
        # tmpInten += gnoise(tmpSig)
        for a in range(len(tmp_intren)):
            for b in range(len(tmp_intren[a])):
                tmp_intren[a][b] = math.trunc(tmp_intren[a][b])
        det = tmp_intren
        panel_object.detector_array = det / (trans * thick * pix_size_x * pix_size_y / math.pow(ssd, 2) * imon)

    def plot_panel(self, panel_object):
        self.make_real_dist_x_y_waves(panel_object)
        m_sep = self.get_offset(panel_object)
        pix_size_x = panel_object.x_pixel_size
        pix_size_y = panel_object.y_pixel_size
        n_pixels_x = int(panel_object.pixel_num_x)
        n_pixels_y = int(panel_object.pixel_num_y)
        panel_object.beam_center_x_pix = n_pixels_x - (m_sep / pix_size_x)
        panel_object.beam_center_y_pix = n_pixels_y / 2

        if self.k_bctr_cm:
            data_real_dist_x = panel_object.data_real_dist_x
            data_real_dist_y = panel_object.data_real_dist_y
            panel_object.beam_center_x_pix = (data_real_dist_x[n_pixels_x - 1][0] / 10 + (
                    panel_object.beam_center_x_pix - n_pixels_x - 1) * pix_size_x)
            panel_object.beam_center_y_pix = data_real_dist_y[0][int(panel_object.beam_center_y_pix)] / 10
        ssd = self.get_ssd(panel_object)
        self.detector_2q_non_linear(panel_object=panel_object)  # Something to set scale

    def detector_2q_non_linear(self, panel_object):
        lam = self.lambda_val
        tube_width = 8.4
        dim_x = panel_object.pixel_num_x
        dim_y = panel_object.pixel_num_y
        data_real_dist_x = panel_object.data_real_dist_x
        data_real_dist_y = panel_object.data_real_dist_y
        ssd = self.get_ssd(panel_object)

        def find_phi(dx, dy):

            if dx == 0 and dy > 0:
                return math.pi / 2
            elif dx == 0 and dy < 0:
                return 3 * math.pi / 2
            elif dx >= 0 and dy == 0:
                return 0
            elif dx < 0 and dy == 0:
                return math.pi

            phi = math.atan(dx / dy)
            if dx > 0 and dy > 0:
                return phi
            elif (dx < 0 < dy) or (dx < 0 and dy < 0):
                return phi + math.pi
            elif dx > 0 > dy:
                return phi + 2 * math.pi
            else:
                return phi

        def calc_q_val(a_q, b_q):
            dx = data_real_dist_x[a_q][b_q] - dim_x
            dy = data_real_dist_y[a_q][b_q] - dim_y
            dist = math.sqrt(math.pow(dx, 2) + math.sqrt(math.pow(dy, 2)))
            dist = dist / 10
            two_theta = math.atan(dist / ssd)
            q_val = 4 * math.pi / lam * math.sin(two_theta / 2)
            return q_val

        def calc_q_x(a_x, b_x):
            q_val = calc_q_val(a_x, b_x)
            dx = data_real_dist_x[a_x][b_x] - dim_x  # Delta x in mm
            dy = data_real_dist_y[a_x][b_x] - dim_y  # Delta y in mm
            phi = find_phi(dx, dy)

            # get scattering angle to project onto flat detector => Qr = qval*cos(theta)
            dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
            dist = dist / 10  # Convert mm to cm
            two_theta = math.atan(dist / ssd)
            qx = q_val * math.cos(two_theta / 2) * math.cos(phi)
            return qx

        def calc_q_y(a_y, b_y):
            qval = calc_q_val(a_y, b_y)
            dx = data_real_dist_x[a_y][b_y] - dim_x
            dy = data_real_dist_y[a_y][b_y] - dim_y
            phi = find_phi(dx, dy)

            # get scattering angle to project onto flat detector => Qr = qval*cos(theta)
            dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
            dist = dist / 10  # convert mm to cm

            two_theta = math.atan(dist / ssd)
            qy = qval * math.cos(two_theta / 2) * math.sin(phi)
            return qy

        def calc_q_z(a, b):
            q_val = calc_q_val(a, b)
            dx = data_real_dist_x[a][b] - dim_x
            dy = data_real_dist_y[a][b] - dim_y

            dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
            dist = dist / 10  # convert mm to cm

            two_theta = math.atan(dist / ssd)
            qz = q_val * math.sqrt(two_theta / 2)
            return qz

        if self.k_bctr_cm:  # And not the back detector
            # Calculate all the q values
            for a in range(len(panel_object.q_to_t_array)):
                for b in range(len(panel_object.q_to_t_array[0])):
                    panel_object.q_to_t_array[a][b] = calc_q_val(a, b)
            for a in range(len(panel_object.qx_array)):
                for b in range(len(panel_object.qx_array[0])):
                    panel_object.qx_array[a][b] = calc_q_x(a, b)

            for a in range(len(panel_object.qy_array)):
                for b in range(len(panel_object.qy_array[0])):
                    panel_object.qy_array[a][b] = calc_q_y(a, b)

            for a in range(len(panel_object.qz_array)):
                for b in range(len(panel_object.qz_array[0])):
                    panel_object.qz_array[a][b] = calc_q_z(a, b)

    def make_real_dist_x_y_waves(self, panel_object):
        # VC_MakeRealDistXYWaves in IGORPro
        # make the data_realDistX,Y Waves that are needed for the calculation of q
        tmp_array = panel_object.create_tmp_array()
        tube_width = 8.4
        # self.non_linear_correction(data,tmpCalib,tube_width,detStr,destPath)

        # The below is V_NonLinearCorrection in igor
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

        # Params needed to calculate teh real_dist arrays
        other_array_x = panel_object.data_real_dist_x  # The array we are editing
        other_array_y = panel_object.data_real_dist_y  # The array we are editing
        offset = self.get_offset(panel_object=panel_object)
        offset = offset * 10

        # Get the data in the real_dist arrays
        if not horizontal_orientation:
            if self.k_bctr_cm:  # Matches what is in IGOR:
                if 'L' in panel_object.short_name:
                    for a in range(len(other_array_x)):
                        value = offset - (diamX - a - .5) * tube_width - gap / 2
                        for b in range(len(other_array_x[0])):
                            other_array_x[a][b] = value
                else:  # Matches what is in IGOR
                    # If it is on the right
                    for a in range(len(other_array_x)):
                        value = tube_width * (a + .5) + offset + gap / 2
                        for b in range(len(other_array_x[0])):
                            other_array_x[a][b] = value
            else:
                for a in range(len(other_array_x)):
                    value = tube_width * a
                    for b in range(len(other_array_x[0])):
                        other_array_x[a][b] = value
            # Set up the y array for the horizontal orientation
            for a in range(len(other_array_y)):  # Matches what it says in IGOR
                for b in range(len(other_array_y[0])):
                    other_array_y[a][b] = tmp_array[0][a] + tmp_array[1][a] * b + tmp_array[2][a] * b * b
        else:  # If it is a horizontal panel
            if self.k_bctr_cm:
                if 'T' in panel_object.short_name:
                    for a in range(len(other_array_y)):
                        for b in range(len(other_array_y[0])):
                            other_array_y[a][b] = tube_width * (b + .5) + offset + gap / 2
                else:
                    for a in range(len(other_array_y)):
                        for b in range(len(other_array_y[0])):
                            other_array_y[a][b] = offset - (diamy - b - .5) * tube_width - gap / 2
            else:
                for a in range(len(other_array_y)):
                    for b in range(len(other_array_y[0])):
                        other_array_y[a][b] = tube_width * b
            for a in range(len(other_array_x)):
                for b in range(len(other_array_x[0])):
                    other_array_x[a][b] = tmp_array[0][b] + tmp_array[1][b] * a + tmp_array[2][b] * a * a

    # End calculate panel functions

    def reset_mask(self):
        # VC_ResetVCALCMask in Igor Pro
        for panel in self.all_detectors:
            panel.data = np.zeros((len(panel.detector_array), len(panel.detector_array[0])))

    def draw_mask(self, panel_object):
        # VC_DrawVCALCMask in Igor Pro

        offset = self.get_offset(panel_object)
        D2 = self.parent.get_sample_aperture()
        l2 = self.get_l_2(panel_object)

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

    def get_l_2(self,panel_object):
        if 'F' in panel_object.short_name:
            return self.front_carriage.l_2
        else:
            return self.middle_carriage.l_2

    @staticmethod
    def get_offset(panel_object):
        # VCALC_getPanelTranslation in IGOR
        if panel_object.horizontal_orientation:
            return panel_object.verticalOffset
        else:
            return panel_object.lateral_offset

    @staticmethod
    def get_setback(panel_object):
        # VCALC_getPanelTranslation in IGOR
        if panel_object.horizontal_orientation:
            return panel_object.setback
        else:
            return 0

    def get_ssd(self, panel_object):
        # VCALC_getPanelTranslation in IGOR
        if 'F' in panel_object.short_name:
            return self.front_carriage.ssd
        else:
            return self.middle_carriage.ssd
