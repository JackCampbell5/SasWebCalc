import math

import numpy as np

from .InstrumentBase import Instrument
from ..instrument import CALC_TYPE, set_params
from ..instrument import Collimation as BaseCollimation
from ..instrument import Detector as BaseDetector
from ..instrumentJSParams import *


def _create_vsans_dict(is_named: bool = True, has_additional: bool = False):
    """Creates the sub dictionary necessary for the VSANS instrument to work properly and returns the all in 1
    dictionary

    The sub dictionary include presets, beam, collimation, middle_carriage, mid_left_panel, mid_right_panel,
    mid_top_panel, mid_bottom_panel, front_carriage, front_left_panel, front_right_panel, front_top_panel,
    front_bottom_panel, and options

    The additional dictionary's include all_carriage, mid_dq_values, and front_dq_values

    :param Boolean is_named: Whether to include name as the first part of the dictionary
    :param Boolean has_additional: Whether the additional sub dictionary are included
    :return: The dictionary created by the parameters defined
    :rtype: Dict
    """
    vsans_dict = dict()
    vsans_dict["presets"] = {"name": "Presets"} if is_named else {}
    vsans_dict["beam"] = {"name": "Beam"} if is_named else {}
    vsans_dict["collimation"] = {"name": "Collimation"} if is_named else {}
    vsans_dict["middle_carriage"] = {"name": "Middle Carriage"} if is_named else {}
    vsans_dict["mid_left_panel"] = {"name": "Middle Carriage Left Panel"} if is_named else {}
    vsans_dict["mid_right_panel"] = {"name": "Middle Carriage Right Panel"} if is_named else {}
    vsans_dict["mid_top_panel"] = {"name": "Middle Carriage Top Panel"} if is_named else {}
    vsans_dict["mid_bottom_panel"] = {"name": "Middle Carriage Bottom Panel"} if is_named else {}
    vsans_dict["front_carriage"] = {"name": "Front Carriage"} if is_named else {}
    vsans_dict["front_left_panel"] = {"name": "Front Carriage Left Panel"} if is_named else {}
    vsans_dict["front_right_panel"] = {"name": "Front Carriage Right Panel"} if is_named else {}
    vsans_dict["front_top_panel"] = {"name": "Front Carriage Top Panel"} if is_named else {}
    vsans_dict["front_bottom_panel"] = {"name": "Front Carriage Bottom Panel"} if is_named else {}
    vsans_dict["options"] = {}
    if has_additional:
        vsans_dict["all_carriage"] = {}
        vsans_dict["mid_dq_values"] = {}
        vsans_dict["front_dq_values"] = {}
    return vsans_dict


class VSANS(Instrument):
    """ A class to manipulate VSANS calculations and parameters

    :param str self.name: The name of the instrument
    :param dict self.preset: What the preset selected is for the VSANS instrument
    :param dict self.options: The options to return to the JS to change specific parts of the parameters that are not default
    :param Beam self.beam: The beam object that contains info related to the beam section of the params
    :param Collimation self.collimation: The Collimation object that contains info related to the collimation section
        of the params
    :param AllCarriage self.all_carriage: The AllCarriage object that contains info related to some params in the
        MiddleCarriage section of the params
    :param MiddleCarriage self.middle_carriage: The MiddleCarriage object that contains info related to the Middle
        Carriage and middle detector section of the params
    :param FrontCarriage self.front_carriage: The FrontCarriage object that contains info related to the Front
        Carriage and front detectors section of the params
    :param Constants self.constants: The Constants object that contains the constants needed for the VSANS instrument
    """
    class_name = "VSANS"
    name_shown = "VSANS"

    # Constructor for the VSANS instrument
    def __init__(self, name: str | None, params: dict):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        """
        self.name = name if name else "VSANS"
        self.preset = params.get('preset', "19m")
        self.options = {}  # {"type": "options", "category": "", "set_to": }
        self.beam = None
        self.all_carriage = None
        self.collimation = None
        self.middle_carriage = None
        self.front_carriage = None
        self.plot_data = None
        self.detectors = []
        self.constants = VSANSConstants().get_constants(self.preset, _create_vsans_dict(is_named=False))
        # if this is necessary
        # Super is the Instrument class
        super().__init__(name, params)
        params = params["instrument_params"]
        self.load_params(params)

    def load_params(self, old_params: dict):
        """A method that loads the constants of the VSANS Instrument

        :param dict old_params: The dictionary of parameters from the __init__ statement
        """
        params = self.param_restructure(old_params)

        params["temp"] = dict()
        params["temp"]["serverName"] = "vsans.ncnr.nist.gov"
        params["beam"]["frontend_trans_options"] = {"0.02": 0.5, "0.12": 1.0, "0.4": 0.7}
        params["beam"]["lambda_T"] = self.constants.get("lambda_T", 6.2)
        params["beam"]["phi_0"] = self.constants.get("phi_0", 1.82e13)
        # Front carriage constants
        params["front_carriage"]["lr_w"] = 40.3
        params["front_carriage"]["lr_h"] = 100.0
        params["front_carriage"]["tb_w"] = 50.0
        params["front_carriage"]["tb_h"] = 40.3
        params["front_carriage"]["ssd_setback"] = 41.0
        params["front_left_panel"]["beam_center_x"] = 55
        params["front_left_panel"]["beam_center_y"] = 64
        params["front_right_panel"]["beam_center_x"] = -8
        params["front_right_panel"]["beam_center_y"] = 64
        params["front_top_panel"]["beam_center_x"] = 64
        params["front_top_panel"]["beam_center_y"] = -8
        params["front_bottom_panel"]["beam_center_x"] = 64
        params["front_bottom_panel"]["beam_center_y"] = 55
        # Middle Carriage constants
        params["middle_carriage"]["lr_w"] = 40.3
        params["middle_carriage"]["lr_h"] = 100.0
        params["middle_carriage"]["tb_w"] = 50.0
        params["middle_carriage"]["tb_h"] = 40.3
        params["middle_carriage"]["ssd_setback"] = 41.0
        params["mid_left_panel"]["beam_center_x"] = 55
        params["mid_left_panel"]["beam_center_y"] = 64
        params["mid_right_panel"]["beam_center_x"] = -8
        params["mid_right_panel"]["beam_center_y"] = 64
        params["mid_top_panel"]["beam_center_x"] = 64
        params["mid_top_panel"]["beam_center_y"] = -8
        params["mid_bottom_panel"]["beam_center_x"] = 64
        params["mid_bottom_panel"]["beam_center_y"] = 55

        self.load_objects(params)

    def param_restructure(self, old_params: dict):
        """ A method that takes the list of params from the Javascript and assigns it to a dictionary allowing the
        python to assign variables to objects

        :param dict old_params: A dictionary of the values gotten from the js
        :return: An dictionary of the params that has been restructured correctly
        :rtype: Dict
        """

        def _param_get_helper(name: str = "", category: str = "", key: str = "default",
                              default_value: str | float | int | None = None, division: float = 1.0):
            """ Checks if a value exists at a certain key and if not sets the value to none ot be removed later

            :param str name: the dictionary of parameters to get the value from
            :param str key: The name of the key you want the value of
            :param default_value: The default value if none exists at that location in the params dictionary
            :param int division: The number to divide by if necessary for debuting
            :return: The value at the keys position in the dictionary or None
            :rtype: str | None
            """
            help_params = old_params.get(category, {}).get(name, {})
            try:
                result_raw = help_params.get(key, default_value)
                return result_raw / division
            except AttributeError:
                return None
            except (ZeroDivisionError, TypeError):
                # Only reachable if attempting division
                # If it is blank use the default value
                if result_raw == "":
                    return default_value
                return result_raw

        params = _create_vsans_dict(False, True)
        params["preset"] = _param_get_helper(name="presets", category="presets", default_value="19m")
        params["beam"]["wavelength"] = _param_get_helper(name="wavelength", category="beam", default_value=6.0)
        params["beam"]["dlambda"] = _param_get_helper(name="dlambda", category="beam", default_value=0.12)
        params["beam"]["frontend_trans"] = _param_get_helper(name="frontend_trans", category="beam", default_value=1.0)
        params["beam"]["flux"] = _param_get_helper(name="flux", category="beam", default_value=1.362e+11)
        params["beam"]["beam_current"] = _param_get_helper(name="beam_current", category="beam", default_value=1.055e+5)
        params["beam"]["i_sub_zero"] = _param_get_helper(name="i_sub_zero", category="beam", default_value=8.332e+4)
        params["collimation"]["guide_select"] = _param_get_helper(name="guide_select", category="collimation",
                                                                  default_value=0)
        params["collimation"]["source_aperture_js"] = _param_get_helper(name="source_aperture_js",
                                                                        category="collimation", default_value=30.0)
        params["collimation"]["source_distance"] = _param_get_helper(name="source_distance", category="collimation",
                                                                     default_value=2441)
        params["collimation"]["t_filter"] = _param_get_helper(name="t_filter", category="collimation",
                                                              default_value=0.5062523594147008)
        params["collimation"]["t_guide"] = _param_get_helper(name="t_guide", category="collimation", default_value=1)
        params["collimation"]["ext_sample_aperture"] = _param_get_helper(name="ext_sample_aperture",
                                                                         category="collimation", default_value=12.7)
        params["collimation"]["sample_to_ap_gv"] = _param_get_helper(name="sample_to_ap_gv", category="collimation",
                                                                     default_value=22)
        params["collimation"]["sample_to_gv"] = _param_get_helper(name="sample_to_gv", category="collimation",
                                                                  default_value=22)
        params["collimation"]["l_1"] = _param_get_helper(name="l_1", category="collimation", default_value=2419)
        params["collimation"]["a_over_l"] = _param_get_helper(name="a_over_l", category="collimation",
                                                              default_value=0.000001530)
        params["middle_carriage"]["ssd_input"] = _param_get_helper(name="ssd_input", category="middle_carriage",
                                                                   default_value=1900)
        params["middle_carriage"]["ssd"] = _param_get_helper(name="ssd", category="middle_carriage", default_value=1911)
        params["middle_carriage"]["l_2"] = _param_get_helper(name="l_2", category="middle_carriage", default_value=1922)
        params["all_carriage"]["beam_drop"] = _param_get_helper(name="beam_drop", category="middle_carriage",
                                                                default_value=0.9414)
        params["all_carriage"]["beamstop_required"] = _param_get_helper(name="beamstop_required",
                                                                        category="middle_carriage", default_value=2.014)
        params["all_carriage"]["beamstop"] = _param_get_helper(name="beamstop", category="middle_carriage",
                                                               default_value=2)
        params["all_carriage"]["two_theta_min"] = _param_get_helper(name="two_theta_min", category="middle_carriage",
                                                                    default_value=0.001329)
        params["mid_dq_values"]["q_min"] = _param_get_helper(name="q_min", category="middle_carriage",
                                                             default_value=0.001392)
        params["mid_dq_values"]["dqx_min"] = _param_get_helper(name="dqx_min", category="middle_carriage",
                                                               default_value=0.3393)
        params["mid_dq_values"]["dqx_min"] = _param_get_helper(name="dqx_min", category="middle_carriage",
                                                               default_value=0.3412)
        params["mid_dq_values"]["q_max"] = _param_get_helper(name="q_max", category="middle_carriage",
                                                             default_value=0.03818)
        params["mid_dq_values"]["dqx_max"] = _param_get_helper(name="dqx_max", category="middle_carriage",
                                                               default_value=0.05050)
        params["mid_dq_values"]["dqy_max"] = _param_get_helper(name="dqy_max", category="middle_carriage",
                                                               default_value=0.05051)
        params["middle_carriage"]["refBeamCtr_x"] = _param_get_helper(name="refBeamCtr_x", category="middle_carriage",
                                                                      default_value=0)
        params["middle_carriage"]["refBeamCtr_y"] = _param_get_helper(name="refBeamCtr_y", category="middle_carriage",
                                                                      default_value=0)
        params["mid_left_panel"]["offset"] = _param_get_helper(name="offset", category="mid_left_panel",
                                                                       default_value=-6)
        params["mid_left_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="mid_left_panel",
                                                               default_value=0.003822)
        params["mid_left_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="mid_left_panel",
                                                               default_value=-0.02545)
        params["mid_right_panel"]["offset"] = _param_get_helper(name="offset",
                                                                        category="mid_right_panel", default_value=-5.5)
        params["mid_right_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="mid_right_panel",
                                                                default_value=-0.002622)
        params["mid_right_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="mid_right_panel",
                                                                default_value=0.01901)
        params["mid_right_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_right_panel",
                                                                default_value=0.02854)
        params["mid_right_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_right_panel",
                                                                default_value=0.02809)
        params["mid_top_panel"]["offset"] = _param_get_helper(name="offset", category="mid_top_panel",
                                                                      default_value=0)
        params["mid_top_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_top_panel", default_value=0)
        params["mid_top_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_top_panel", default_value=0)
        params["mid_bottom_panel"]["offset"] = _param_get_helper(name="offset",
                                                                         category="mid_bottom_panel", default_value=0)
        params["mid_bottom_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_bottom_panel",
                                                                 default_value=0)
        params["mid_bottom_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_bottom_panel",
                                                                 default_value=0)
        params["front_dq_values"]["q_min"] = _param_get_helper(name="q_min", category="front_carriage",
                                                               default_value=0.01875)
        params["front_dq_values"]["dqx_min"] = _param_get_helper(name="dqx_min", category="front_carriage",
                                                                 default_value=0.05496)
        params["front_dq_values"]["dqy_min"] = _param_get_helper(name="dqy_min", category="front_carriage",
                                                                 default_value=0.05503)
        params["front_dq_values"]["q_max"] = _param_get_helper(name="q_max", category="front_carriage",
                                                               default_value=0.1826)
        params["front_dq_values"]["dqx_max"] = _param_get_helper(name="dqx_max", category="front_carriage",
                                                                 default_value=0.04906)
        params["front_dq_values"]["dqy_max"] = _param_get_helper(name="dqy_max", category="front_carriage",
                                                                 default_value=0.04906)
        params["front_carriage"]["ssd_input"] = _param_get_helper(name="ssd_input", category="front_carriage",
                                                                  default_value=400)
        params["front_carriage"]["ssd"] = _param_get_helper(name="ssd", category="front_carriage", default_value=411)
        params["front_carriage"]["refBeamCtr_x"] = _param_get_helper(name="refBeamCtr_x", category="front_carriage",
                                                                     default_value=0)
        params["front_carriage"]["refBeamCtr_y"] = _param_get_helper(name="refBeamCtr_y", category="front_carriage",
                                                                     default_value=0)
        params["front_left_panel"]["offset"] = _param_get_helper(name="offset",
                                                                         category="front_left_panel",
                                                                         default_value=-9.24)
        params["front_left_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="front_left_panel",
                                                                 default_value=-0.02538)
        params["front_left_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="front_left_panel",
                                                                 default_value=-0.1253)
        params["front_left_panel"]["match_button"] = _param_get_helper(name="match_button", category="front_left_panel",
                                                                       default_value=False)
        params["front_right_panel"]["offset"] = _param_get_helper(name="offset",
                                                                          category="front_right_panel",
                                                                          default_value=6.766)
        params["front_right_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="front_right_panel",
                                                                  default_value=0.01875)
        params["front_right_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="front_right_panel",
                                                                  default_value=0.1188)
        params["front_right_panel"]["match_button"] = _param_get_helper(name="match_button",
                                                                        category="front_right_panel",
                                                                        default_value=False)
        params["front_top_panel"]["offset"] = _param_get_helper(name="offset",
                                                                        category="front_top_panel", default_value=0)
        params["front_top_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="front_top_panel",
                                                                default_value=0.001147)
        params["front_top_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="front_top_panel",
                                                                default_value=0.09234)
        params["front_top_panel"]["match_button"] = _param_get_helper(name="match_button", category="front_top_panel",
                                                                      default_value=False)
        params["front_bottom_panel"]["offset"] = _param_get_helper(name="offset",
                                                                           category="front_bottom_panel",
                                                                           default_value=0)
        params["front_bottom_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="front_bottom_panel",
                                                                   default_value=-0.003139)
        params["front_bottom_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="front_bottom_panel",
                                                                   default_value=-0.09432)
        params["front_bottom_panel"]["match_button"] = _param_get_helper(name="match_button",
                                                                         category="front_bottom_panel",
                                                                         default_value=False)
        return self._remove_nones(params)

    def load_objects(self, params: dict):
        """A function that creates the objects necessary for the calculations

        Create objects beam_stops, detectors, collimation, and wavelength

        :param dict params: A dictionary of parameters to send to the initialization of the objects
        """
        self.beam = Beam(self, params.get('beam', {}))
        self.collimation = Collimation(self, params.get('collimation', {}))
        self.all_carriage = AllCarriage(self, params.get('all_carriage', {}))
        middle_carriage_params = {"middle_carriage": params.get('middle_carriage', {}),
                                  "mid_dq_values": params.get("mid_dq_values", {}),
                                  "mid_left_panel": params.get("mid_left_panel", {}),
                                  "mid_right_panel": params.get("mid_right_panel", {}),
                                  "mid_top_panel": params.get("mid_top_panel", {}),
                                  "mid_bottom_panel": params.get("mid_bottom_panel", {}),
                                  }
        self.middle_carriage = MiddleCarriage(self, middle_carriage_params)
        front_carriage_params = {"front_carriage": params.get('front_carriage', {}),
                                 "front_dq_values": params.get("front_dq_values", {}),
                                 "front_left_panel": params.get("front_left_panel", {}),
                                 "front_right_panel": params.get("front_right_panel", {}),
                                 "front_top_panel": params.get("front_top_panel", {}),
                                 "front_bottom_panel": params.get("front_bottom_panel", {}),
                                 }
        self.front_carriage = FrontCarriage(self, front_carriage_params)

    def calculate_objects(self):
        """Runs the calculate method of all the objects created in load objects"""
        self.beam.calculate_beam()
        self.collimation.calculate_collimation()
        self.all_carriage.calculate_all_Carriage()
        self.middle_carriage.calculate_carriage()
        self.front_carriage.calculate_carriage()

    def compile_detectors(self):
        """A helper method to take the detector arrays from the Carriage objects and create a list."""

        for panel in [self.middle_carriage.left_panel, self.middle_carriage.right_panel, self.middle_carriage.top_panel,
                      self.middle_carriage.bottom_panel, self.front_carriage.left_panel, self.front_carriage.top_panel,
                      self.front_carriage.right_panel, self.front_carriage.bottom_panel]:
            self.detectors.append(panel.detectors)

    def calculate_plots(self):
        """A method that  takes in all the params from the other classes needed to calculate the plot data and passes it
        as a parameter to the innit statement of the PLotData class"""
        plot_params = dict()
        plot_params["middle_carriage"] = self.middle_carriage
        plot_params["mid_left_panel"] = self.middle_carriage.left_panel
        plot_params["mid_right_panel"] = self.middle_carriage.right_panel
        plot_params["mid_top_panel"] = self.middle_carriage.top_panel
        plot_params["mid_bottom_panel"] = self.middle_carriage.bottom_panel
        plot_params["front_carriage"] = self.front_carriage
        plot_params["front_left_panel"] = self.front_carriage.left_panel
        plot_params["front_right_panel"] = self.front_carriage.right_panel
        plot_params["front_top_panel"] = self.front_carriage.top_panel
        plot_params["front_bottom_panel"] = self.front_carriage.bottom_panel
        plot_params["lambda_val"] = self.get_wavelength()
        self.plot_data = PlotData(parent=self, params=plot_params)
        self.plot_data.run_plot_data()

    # Get methods After here
    def get_wavelength(self) -> float:
        """Gets the wavelength parameter from the beam object

        :return: The values of the wavelength parameter
        :rtype: Float
        """
        return self.beam.wavelength

    # Get methods After here
    def get_wavelength_spread(self) -> float:
        """Gets the wavelength parameter from the beam object

        :return: The values of the wavelength parameter
        :rtype: Float
        """
        return self.beam.dlambda

    def get_beam_stop_diameter(self, index=0):
        return self.all_carriage.beamstop_required

    def get_l_1(self) -> float:
        """Gets the l_1 parameter from the collimation object

        :return: The values of the l_1 parameter
        :rtype: Float
        """
        return self.collimation.l_1

    def get_l_2(self) -> float:
        """Gets the l_2 parameter from the middle carriage object

        :return: The values of the l_2 parameter
        :rtype: Float
        """
        return self.middle_carriage.l_2

    def get_source_aperture_size(self):
        return self.get_source_aperture() / 2.0

    def get_source_aperture(self) -> float:
        """Gets the source aperture parameter from the collimation object

        :return: The values of the source aperture parameter
        :rtype: Float
        """
        return self.collimation.source_aperture

    def get_sample_aperture_size(self):
        return self.get_sample_aperture() / 2.0

    def get_sample_aperture(self) -> float:
        """Gets the sample aperture parameter from the collimation object

        :return: The values of the sample aperture parameter
        :rtype: Float
        """
        return self.collimation.sample_aperture

    def sas_calc(self) -> CALC_TYPE:
        """ The main function that runs all the calculation though the calculate objects and calculate plot methods and
        returns the results

        Makes a user inaccessible sub dictionary witch contains the results to be sent back to the instrument JS

        :return: A dictionary of the calculation results
        :rtype: Dict
        """
        # Calculate all the objects
        self.calculate_objects()
        self.calculate_plots()
        self.compile_detectors()
        for index in range(len(self.detectors)):
            panel = self.detectors[index]
            self.slicer_params = {'coeff': 10000, 'x_pixels': panel.x_dim, 'y_pixels': panel.y_dim}
            self.calculate_slicer(index)
        # Calculate all the Plots
        user_inaccessible = _create_vsans_dict(is_named=False)
        user_inaccessible["beam"]["wavelength"] = self.beam.wavelength
        user_inaccessible["beam"]["dlambda"] = self.beam.dlambda
        user_inaccessible["beam"]["frontend_trans"] = self.beam.frontend_trans
        user_inaccessible["beam"]["flux"] = self.beam.flux
        user_inaccessible["beam"]["beam_current"] = self.beam.beam_current
        user_inaccessible["beam"]["i_sub_zero"] = self.beam.i_sub_zero
        user_inaccessible["collimation"]["guide_select"] = self.collimation.guide_select
        user_inaccessible["collimation"]["source_aperture_js"] = self.collimation.source_aperture_js
        user_inaccessible["collimation"]["source_distance"] = self.collimation.source_distance
        user_inaccessible["collimation"]["t_filter"] = self.collimation.t_filter
        user_inaccessible["collimation"]["t_guide"] = self.collimation.t_guide
        user_inaccessible["collimation"]["ext_sample_aperture"] = self.collimation.ext_sample_aperture
        user_inaccessible["collimation"]["sample_to_ap_gv"] = self.collimation.sample_to_ap_gv
        user_inaccessible["collimation"]["sample_to_gv"] = self.collimation.sample_to_gv
        user_inaccessible["collimation"]["l_1"] = self.collimation.l_1
        user_inaccessible["collimation"]["a_over_l"] = self.collimation.a_over_l
        user_inaccessible["middle_carriage"]["ssd_input"] = self.middle_carriage.ssd_input
        user_inaccessible["middle_carriage"]["ssd"] = self.middle_carriage.ssd
        user_inaccessible["middle_carriage"]["l_2"] = self.middle_carriage.l_2
        user_inaccessible["middle_carriage"]["beam_drop"] = self.all_carriage.beam_drop
        user_inaccessible["middle_carriage"]["beamstop_required"] = self.all_carriage.beamstop_required
        user_inaccessible["middle_carriage"]["beamstop"] = self.all_carriage.beamstop
        user_inaccessible["middle_carriage"]["two_theta_min"] = self.all_carriage.two_theta_min
        user_inaccessible["middle_carriage"]["q_min"] = self.middle_carriage.dq_calc.q_min
        user_inaccessible["middle_carriage"]["dqx_min"] = self.middle_carriage.dq_calc.dqx_min
        user_inaccessible["middle_carriage"]["dqy_min"] = self.middle_carriage.dq_calc.dqy_min
        user_inaccessible["middle_carriage"]["q_max"] = self.middle_carriage.dq_calc.q_max
        user_inaccessible["middle_carriage"]["dqx_max"] = self.middle_carriage.dq_calc.dqx_max
        user_inaccessible["middle_carriage"]["dqy_max"] = self.middle_carriage.dq_calc.dqy_max
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = self.middle_carriage.refBeamCtr_x
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = self.middle_carriage.refBeamCtr_y
        user_inaccessible["mid_left_panel"]["offset"] = self.middle_carriage.left_panel.offset
        user_inaccessible["mid_left_panel"]["qx_max"] = self.middle_carriage.left_panel.qx_max
        user_inaccessible["mid_left_panel"]["qx_min"] = self.middle_carriage.left_panel.qx_min
        user_inaccessible["mid_right_panel"]["offset"] = self.middle_carriage.right_panel.offset
        user_inaccessible["mid_right_panel"]["qx_min"] = self.middle_carriage.right_panel.qx_min
        user_inaccessible["mid_right_panel"]["qx_max"] = self.middle_carriage.right_panel.qx_max
        user_inaccessible["mid_right_panel"]["qy_min"] = self.middle_carriage.right_panel.qy_min
        user_inaccessible["mid_right_panel"]["qy_max"] = self.middle_carriage.right_panel.qy_max
        user_inaccessible["mid_top_panel"]["offset"] = self.middle_carriage.top_panel.offset
        user_inaccessible["mid_top_panel"]["qy_min"] = self.middle_carriage.top_panel.qy_min
        user_inaccessible["mid_top_panel"]["qy_max"] = self.middle_carriage.top_panel.qy_max
        user_inaccessible["mid_bottom_panel"]["offset"] = self.middle_carriage.bottom_panel.offset
        user_inaccessible["mid_bottom_panel"]["qy_max"] = self.middle_carriage.bottom_panel.qy_max
        user_inaccessible["mid_bottom_panel"]["qy_min"] = self.middle_carriage.bottom_panel.qy_min
        user_inaccessible["front_carriage"]["q_min"] = self.front_carriage.dq_calc.q_min
        user_inaccessible["front_carriage"]["dqx_min"] = self.front_carriage.dq_calc.dqx_min
        user_inaccessible["front_carriage"]["dqy_min"] = self.front_carriage.dq_calc.dqy_min
        user_inaccessible["front_carriage"]["q_max"] = self.front_carriage.dq_calc.q_max
        user_inaccessible["front_carriage"]["dqx_max"] = self.front_carriage.dq_calc.dqx_max
        user_inaccessible["front_carriage"]["dqy_max"] = self.front_carriage.dq_calc.dqy_max
        user_inaccessible["front_carriage"]["ssd_input"] = self.front_carriage.ssd_input
        user_inaccessible["front_carriage"]["ssd"] = self.front_carriage.ssd
        user_inaccessible["front_carriage"]["refBeamCtr_x"] = self.front_carriage.refBeamCtr_x
        user_inaccessible["front_carriage"]["refBeamCtr_y"] = self.front_carriage.refBeamCtr_y
        user_inaccessible["front_left_panel"]["offset"] = self.front_carriage.left_panel.offset
        user_inaccessible["front_left_panel"]["qx_max"] = self.front_carriage.left_panel.qx_max
        user_inaccessible["front_left_panel"]["qx_min"] = self.front_carriage.left_panel.qx_min
        user_inaccessible["front_left_panel"]["match_button"] = self.front_carriage.left_panel.match_button
        user_inaccessible["front_right_panel"]["offset"] = self.front_carriage.right_panel.offset
        user_inaccessible["front_right_panel"]["qx_min"] = self.front_carriage.right_panel.qx_min
        user_inaccessible["front_right_panel"]["qx_max"] = self.front_carriage.right_panel.qx_max
        user_inaccessible["front_right_panel"]["match_button"] = self.front_carriage.right_panel.match_button
        user_inaccessible["front_top_panel"]["offset"] = self.front_carriage.top_panel.offset
        user_inaccessible["front_top_panel"]["qy_min"] = self.front_carriage.top_panel.qy_min
        user_inaccessible["front_top_panel"]["qy_max"] = self.front_carriage.top_panel.qy_max
        user_inaccessible["front_top_panel"]["match_button"] = self.front_carriage.top_panel.match_button
        user_inaccessible["front_bottom_panel"]["offset"] = self.front_carriage.bottom_panel.offset
        user_inaccessible["front_bottom_panel"]["qy_max"] = self.front_carriage.bottom_panel.qy_max
        user_inaccessible["front_bottom_panel"]["qy_min"] = self.front_carriage.bottom_panel.qy_min
        user_inaccessible["front_bottom_panel"]["match_button"] = self.front_carriage.bottom_panel.match_button
        python_return = {"user_inaccessible": user_inaccessible, "data": {}}
        for i, slicer in enumerate(self.slicer):
            python_return["data"][i] = {}
            python_return["data"][i]["nCells"] = slicer.n_cells.tolist()
            python_return["data"][i]["qsq"] = slicer.d_sq.tolist()
            python_return["data"][i]["sigmaAve"] = slicer.sigma_ave.tolist()
            python_return["data"][i]["qAverage"] = slicer.q_average.tolist()
            python_return["data"][i]["sigmaQ"] = slicer.sigma_q.tolist()
            python_return["data"][i]["fSubs"] = slicer.f_subs.tolist()
            python_return["data"][i]["qxValues"] = slicer.qx_values.tolist()
            python_return["data"][i]["qyValues"] = slicer.qy_values.tolist()
            python_return["data"][i]["q2DValues"] = slicer.q_2d_values.tolist()
            python_return["data"][i]["intensity2D"] = slicer.intensity_2D.tolist()
            python_return["data"][i]["qValues"] = slicer.q_values.tolist()
            python_return["data"][i]["slicer_params"] = slicer.slicer_return()
        if self.options is not {}:
            python_return['options'] = self.options
        return python_return

    def update_source_aperture_with_data(self, results: dict) -> dict:
        """Updates the value of the source aperture based on the guide number and current value gotten from an array
        of params by calling the update_source_aperture method

        :param dict results: A dictionary of params that contains the source_aperture_js and guide_select params
        :return: The results dictionary but with the source aperture updated
        :rtype: Dict
        """
        # Update the number of guides to be correct
        source_aperture_js = results["collimation"]["source_aperture_js"]
        guide_select = results["collimation"]["guide_select"]
        return self.update_source_aperture(results=results, source_aperture_js=source_aperture_js,
                                            guide_select=guide_select)

    @staticmethod
    def update_source_aperture(results: dict | None = None, source_aperture_js: str = '0.0', guide_select: str = '0'):
        """Updates the value of the source aperture based on the number of guides

        :param dict results: A dictionary to output the results
        :param str source_aperture_js: The string value of the source aperture
        :param str guide_select: The string value of the number of guides
        :return: The results dictionary
        :rtype: Dict
        """
        results = {"collimation": {}, "options": {}} if results is None else results
        if guide_select == '0':
            valid_ops = ['7.5', '15.0', '30.0']
            if not source_aperture_js in valid_ops:
                source_aperture_js = '30.0'
        elif guide_select == 'CONV_BEAMS':
            if source_aperture_js != '6.0':
                source_aperture_js = '6.0'
            valid_ops = ['6.0']
        else:
            if source_aperture_js != '60.0':
                source_aperture_js = '60.0'
            valid_ops = ['60.0']
        results["collimation"]["source_aperture_js"] = source_aperture_js
        results["options"]["collimation+source_aperture_js"] = {"type": "options", "set_to": valid_ops}
        return results

    @staticmethod
    def get_js_params():
        """Creates a dictionary of js element_parameters to create html elements for the NG7SANS

        params[category][elementName] = {element_parameters}

        + **User editable elements:** sampleTable, wavelengthInput, wavelengthSpread, guideConfig, source_aperture,
          sampleAperture,customAperture, sDDInputBox, sDDDefaults, offsetInputBox and offsetDefaults

        + **Read only elements:** beamFlux, figureOfMerit, attenuators, attenuationFactor,
          sSD, sDD, beamDiameter, beamStopSize, minimumQ, maximumQ, maximumVerticalQ, maximumHorizontalQ,
          source_apertures, and wavelength_ranges

        + **element_parameters**: name, default, type_val, unit, readonly, options, step, range_id,hidden, lower_limit,
          and upper_limit

        :return: Completed dictionary params[category][paramName] = js_element_array
        :rtype: Dict
        """
        # TODO find all the upper and lower limits of the ones set to None
        params = _create_vsans_dict()
        params["presets"]["preset"] = create_number_select(name="presets", options=["19m", "16m", "11m", "4.5m"],
                                                           default="19m", extra="19m")  # The Extra parameter saves
        # the previous value of the preset, so we can check if it has changed
        params["beam"]["wavelength"] = create_wavelength_input(lower_limit=None, upper_limit=None)
        params["beam"]["dlambda"] = create_wavelength_spread(options=[0.02, 0.12, 0.4], default=0.12)
        params["beam"]["frontend_trans"] = create_number_output(name="Frontend Trans", default=1.0,
                                                                options=[0.5, 1.0, 0.7], unit=None)
        params["beam"]["flux"] = create_number_output(name="Flux", unit="Φ", default=1.362e+11)
        params["beam"]["beam_current"] = create_number_output(name="Beam Current", unit="1/s", default=1.055e+5)
        params["collimation"]["guide_select"] = create_guide_config(
            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "CONV_BEAMS"], extra=0)
        params["collimation"]["source_aperture_js"] = create_source_aperture(unit="mm", options=[7.5, 15.0, 30.0],
                                                                             default=30.0)
        params["collimation"]["source_distance"] = create_number_output(name="Source distance", unit="cm", default=2441)
        params["collimation"]["t_filter"] = create_number_output(name="T_filter", unit=None, default=0.5062523594147008)
        params["collimation"]["t_guide"] = create_number_output(name="T_guide", unit=None, default=1)
        params["collimation"]["ext_sample_aperture"] = create_number_input(name="Ext. Sample aperture", unit="mm",
                                                                           default=12.7, step=0.1)
        params["collimation"]["sample_to_ap_gv"] = create_number_input(name="Sample ap. to GV", unit="cm", default=22)
        params["collimation"]["sample_to_gv"] = create_number_input(name="Sample to GV", unit="cm", default=11)
        params["collimation"]["l_1"] = create_number_output(name="L1", unit="cm", default=2419)
        params["collimation"]["a_over_l"] = create_number_output(name="A_1A_2/L_1", unit=None, default=0.000001530)
        # Middle Carriage
        params["middle_carriage"]["ssd_input"] = create_number_input(name="SDD input", unit="cm", default=1900)
        params["middle_carriage"]["ssd"] = create_number_input(name="SSD", unit="cm", default=1911, readonly=True)
        params["middle_carriage"]["l_2"] = create_number_output(name="l_2", unit="cm", default=1922)
        params["middle_carriage"]["beam_drop"] = create_number_output(name="Beam Drop", unit="cm", default=0.9414)
        params["middle_carriage"]["beamstop_required"] = create_number_output(name="Beamstop Required", unit="inch",
                                                                              default=2.014)
        params["middle_carriage"]["beamstop"] = create_number_select(name="beamstop", unit="inch", options=[2, 3, 4],
                                                                     default=2)
        params["middle_carriage"]["two_theta_min"] = create_number_output(name="2θ_min", unit="rad", default=0.001329)
        params["middle_carriage"]["q_min"] = create_number_output(name="Q_min", unit="1/Å", default=0.001392)
        params["middle_carriage"]["dqx_min"] = create_number_output(name="(ΔQ/Qmin)_x", default=0.3393)
        params["middle_carriage"]["dqy_min"] = create_number_output(name="(ΔQ/Q_min)_y", default=0.3412)
        params["middle_carriage"]["q_max"] = create_number_output(name="Qmax", unit="1/Å", default=0.03818)
        params["middle_carriage"]["dqx_max"] = create_number_output(name="(ΔQ/Q_max)_x", default=0.05050)
        params["middle_carriage"]["dqy_max"] = create_number_output(name="(ΔQ/Q_max)_y", default=0.05051)
        params["middle_carriage"]["refBeamCtr_x"] = create_number_input(name="Ref Beam Ctr_x", default=0, step=0.1,
                                                                        unit="cm")
        params["middle_carriage"]["refBeamCtr_y"] = create_number_input(name="Ref Beam Ctr_y", default=0, step=0.1,
                                                                        unit="cm")
        params["mid_left_panel"]["offset"] = create_number_input(name="Lateral Offset", unit="cm", default=-6)
        params["mid_left_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.003822)
        params["mid_left_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.02545)
        params["mid_right_panel"]["offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                          default=-5.5)
        params["mid_right_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.002622)
        params["mid_right_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.01901)
        params["mid_right_panel"]["qy_min"] = create_number_output(name="Q_bottom", unit="1/Å", default=-0.02854)
        params["mid_right_panel"]["qy_max"] = create_number_output(name="Qtop", unit="1/Å", default=0.02809)
        params["mid_top_panel"]["offset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["mid_top_panel"]["qy_min"] = create_number_output(name="Qbottom", unit="1/Å", default=0.0)
        params["mid_top_panel"]["qy_max"] = create_number_output(name="q_top", unit="1/Å", default=0.0)
        params["mid_bottom_panel"]["offset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["mid_bottom_panel"]["qy_max"] = create_number_output(name="Q_Top", unit="1/Å", default=-0.0)
        params["mid_bottom_panel"]["qy_min"] = create_number_output(name="Q_Bottom", unit="1/Å", default=-0.0)

        # Front Carriage
        params["front_carriage"]["q_min"] = create_number_output(name="Qmin", unit="1/Å", default=0.01875)
        params["front_carriage"]["dqx_min"] = create_number_output(name="(ΔQ/Q_min)_x", unit="1/Å", default=0.05496)
        params["front_carriage"]["dqy_min"] = create_number_output(name="(ΔQ/_Qmin)_y", unit="1/Å", default=0.05503)
        params["front_carriage"]["q_max"] = create_number_output(name="Q_max", unit="1/Å", default=0.1826)
        params["front_carriage"]["dqx_max"] = create_number_output(name="(ΔQ/Q_max)_x", unit="1/Å", default=0.04906)
        params["front_carriage"]["dqy_max"] = create_number_output(name="(ΔQ/_Qmax)_y", unit="1/Å", default=0.04906)
        params["front_carriage"]["ssd_input"] = create_number_input(name="SSD Input", unit="cm", default=400)
        params["front_carriage"]["ssd"] = create_ssd(default=411, readonly=True)
        params["front_carriage"]["refBeamCtr_x"] = create_number_input(name="Ref Beam Ctr X", unit="cm", default=0)
        params["front_carriage"]["refBeamCtr_y"] = create_number_input(name="Ref Beam Ctr Y", unit="cm", default=0)
        params["front_left_panel"]["offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                           default=-9.24)
        params["front_left_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.02538)
        params["front_left_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.1253)
        params["front_left_panel"]["match_button"] = create_checkbox(name="Match to left edge of ML?", default=False)
        params["front_right_panel"]["offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                            default=6.766)
        params["front_right_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=0.01875)
        params["front_right_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.1188)
        params["front_right_panel"]["match_button"] = create_checkbox(name="Match right edge to of MR", default=False)
        params["front_top_panel"]["offset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["front_top_panel"]["qy_min"] = create_number_output(name="Qbottom", unit="1/Å", default=0.001147)
        params["front_top_panel"]["qy_max"] = create_number_output(name="q_top", unit="1/Å", default=0.09234)
        params["front_top_panel"]["match_button"] = create_checkbox(name="Match Top Edge to MR", default=False)
        params["front_bottom_panel"]["offset"] = create_number_input(name="Vertical Offset", unit="cm",
                                                                             default=0)
        params["front_bottom_panel"]["qy_max"] = create_number_output(name="Q_Top", unit="1/Å", default=-0.003139)
        params["front_bottom_panel"]["qy_min"] = create_number_output(name="Q_Bottom", unit="1/Å", default=-0.09432)
        params["front_bottom_panel"]["match_button"] = create_checkbox(name="Match Bottom Edge of MR", default=False)

        # Add hidden params
        params["hidden"] = {}
        constants = VSANSConstants()
        params["hidden"]["19m"] = constants.get_constants('19m')
        params["hidden"]["16m"] = constants.get_constants('16m')
        params["hidden"]["11m"] = constants.get_constants('11m')
        params["hidden"]["4.5m"] = constants.get_constants('4.5m')

        params = check_params(params=params)
        return params

    def get_source_to_sample_aperture_distance(self):
        return self.collimation.l_1

    def get_sample_to_detector_distance(self):
        return self.middle_carriage.l_2


class Beam:
    """A class for storing and manipulating Beam related data.

    :param VSANS self.parent: The parent VSANS object
    :param str self.name: The name of the class
    :param float self.wavelength: The wavelength or lambda value
    :param float self.dlambda: The dlambda value from the JS
    :param float self.lambda_T: The lambdaT value from the JS
    :param float self.phi_0:
    :param float self.frontend_trans:
    :param float self.flux:
    :param float self.beam_current:
    :param float self.i_sub_zero:
    :param dict self.frontend_trans_options: A dictionary of options for front end trans baced on dlambda
    """

    def __init__(self, parent: VSANS, params: dict, name: str = "beam"):
        """ Creates object parameters for Beam class and runs set params method

        :param VSANS parent: The VSANS instance this Beam is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str name: The name of the class
        :return: None as it just sets the parameters
        :rtype: None
        """
        self.parent = parent
        self.name = name
        self.wavelength = 0  # Known as lamda in the js
        self.dlambda = 0.0
        self.lambda_T = 0.0
        self.phi_0 = 0.0
        self.frontend_trans = 0.0
        self.flux = 0.0
        self.beam_current = 0.0
        self.i_sub_zero = 0.0  # or Incident_Intensity
        self.frontend_trans_options = {}
        set_params(instance=self, params=params)

    def dlambda_check_lambda(self):
        """ Makes sure the value of wavelength is correct based off dlambda"""
        if self.dlambda == 0.02:
            self.wavelength = 4.75
        elif self.dlambda == 0.4:
            self.wavelength = 5.3
        else:
            self.calculate_wavelength()

    def calculate_wavelength(self):
        """Corrects the value of wavelength if it is in the wrong range"""
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
        """ Calculates the value of flux from lambda_T wavelength, and dlambda"""
        lfrac = self.lambda_T / self.wavelength
        self.flux = (self.dlambda * np.pow(lfrac, 4) * np.exp(-np.pow(lfrac, 2)) * self.phi_0) / 2.0 * np.pi

    def calculate_beam_current(self):
        """Calculates the current beam value by getting the calculated t_filter value"""
        self.parent.collimation.calculate_t_filter()
        self.beam_current = self.frontend_trans * self.parent.collimation.t_filter

    def calculate_iSub0(self):
        """Calculates the value of i sub 0 from sample aperture and the current beam value"""
        collimation = self.parent.collimation
        collimation.calculate_sample_aperture()
        self.i_sub_zero = self.beam_current / (np.pi * np.pow(collimation.sample_aperture / 2.0, 2))

    def calculate_beam(self):
        """Runs all the calculation methods nessasary to calculate the beam object"""
        self.dlambda_check_lambda()
        self.calculate_frontend_trans()
        self.calculate_flux()
        self.calculate_beam_current()
        self.calculate_iSub0()


class Collimation(BaseCollimation):
    """A class for storing and manipulating Beam related data.

    :param VSANS self.parent: The parent VSANS object
    :param str self.name: The name of the class
    :param int self.guide_select: The value of the js guide select dropdown
    :param int self.num_guides: The number of guides
    :param boolean self.cov_beams: Whether there were cov_beams instead of guides
    :param str self.source_aperture_js: The source aperture str directly from the js
    :param int self.source_aperture: The aperture of the source you are using
    :param int self.source_distance: The distance from the sources
    :param array self.source_distance_options: All the options for source aperture
    :param int self.t_filter: The calculated t filter value
    :param int self.t_guide: The calculated t_guide value
    :param int self.sample_aperture: The aperture of the sample
    :param int self.ext_sample_aperture: A constant of the extended sample aperture
    :param int self.sample_to_ap_gv: The sample to ap_gv distance
    :param int self.sample_to_gv: The sample to gv distance
    :param int self.l_1: The value of 1_1
    :param int self.a_over_l: The value of a over l_1
    """

    def __init__(self, parent: VSANS, params: dict, name: str = "collimation"):
        """Creates object parameters for Collimation class and runs set params method

        Sets object parameters self.parent, self.name, self.guide_select, self.num_guides, self.cov_beams,
        self.source_aperture_js, self.source_aperture, self.source_distance, self.source_distance_options,
        self.t_filter, self.t_guide, self.sample_aperture, self.ext_sample_aperture, self.sample_to_ap_gv,
        self.sample_to_gv, self.l_1, and self.a_over_l

        :param VSANS parent: The VSANS instance this Collimation is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str name: The name of the class
        :return: None as it just sets the parameters
        :rtype: None
        """
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
        super().__init__(parent, params)

    def get_number_of_guides(self) -> int:
        """Decides if guide select value is CONV BEAMS or NARROW SLITS and if not makes it the int value of what was
        selected"""
        self.num_guides = 0 if self.guide_select in ["CONV_BEAMS", "NARROW_SLITS"] else int(self.guide_select)
        return self.num_guides

    def calculate_source_aperture(self):
        """Calculates the value of the source aperture from the value gotten from JS"""
        self.source_aperture = float(self.source_aperture_js) / 10.0

    def calculate_source_distance(self):
        """Calculates the source distance from whatever the number of guides index is in the source_distance_options"""
        self.source_distance = self.source_distance_options[self.num_guides]

    def calculate_t_filter(self):
        """Calculates the value of t_filter from the beam.Wavelength value

        Is run from the beam.calculate_beam_current() method as it is needed for that calculation"""
        lambda_val = self.parent.get_wavelength()
        self.t_filter = np.exp(-0.371 - 0.0305 * lambda_val - 0.00352 * np.pow(lambda_val, 2))

    def calculate_t_guide(self):
        """Calculates the t_guide value using the value for the number of guides"""
        self.t_guide = np.pow(0.97, self.num_guides)

    def calculate_sample_aperture(self):
        """Calculates the sample aperture value from the ext_sample_aperture"""
        self.sample_aperture = self.ext_sample_aperture / 10.0

    def calculate_l_1(self):
        """Calculates the l_1 value from source distance and sample_to_ap_gv value"""
        self.l_1 = self.source_distance - self.sample_to_ap_gv

    def calculate_a_over_l(self):
        """Calculates the value of a_over_l from the source and sample aperture as well as l_1"""
        self.a_over_l = np.pow((math.pi / 4.0 * self.source_aperture * self.sample_aperture / self.l_1), 2)

    def calculate_collimation(self):
        """Runs all the calculation methods nessasary to calculate the collimation object"""
        self.get_number_of_guides()
        self.calculate_source_aperture()
        self.calculate_source_distance()
        self.calculate_t_guide()
        self.calculate_sample_aperture()
        self.calculate_l_1()
        self.calculate_a_over_l()


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

    def __init__(self, parent: VSANS, params: dict, name: str = "all_carriage"):
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
    def __init__(self, parent: VSANS, params: dict, name: str = "middle_carriage"):
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


class DqCalculator:
    """A class for storing and manipulating Beam related data.

    :param FrontCarriage or MiddleCarriage self.parent: The parent FrontCarriage or MiddleCarriage object
    :param str self.name: The name of the class
    :param float self.q_min: The minimum value for Q
    :param method self.calculate_q_min: The method used to calculate the min q value based on which carriage it is in
    :param float self.dqx_min: The min x dq value
    :param float self.dqy_min: The min y dq value
    :param float self.q_max: The max q value
    :param float self.dqx_max: The max x dq value
    :param float self.dqy_max: The max y dq value
    :param float self.dq_geometric: The geometric dq value
    :param float self.dq_wavelength: The wavelength dq value
    :param float self.dq_gravity: The gravity dq value
    """

    def __init__(self, parent: Carriage, params: dict):
        """ Creates object parameters for Dq Calculator class and runs set params method

        :param FrontCarriage or MiddleCarriage parent: The VSANS instance this Beam is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        """
        self.parent = parent
        self.carriages = self.parent.parent.all_carriage

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
        """Updates the local copy of the dq geometric, wavelength and gravity to the one in the all carriage class"""
        self.dq_geometric = self.carriages.dq_geometric
        self.dq_wavelength = self.carriages.dq_wavelength
        self.dq_gravity = self.carriages.dq_gravity

    def _calculate_dq(self, q: np.ndarray | float = 0.0, y_value: bool = False):
        """A private helper method that runs dq calculations using the dq gravity, wavelength, and geometric values"""
        addition = np.pow(self.dq_gravity, 2) if y_value else 0.0
        return np.sqrt(np.pow(self.dq_geometric, 2) + np.pow(self.dq_wavelength * q, 2) + addition) / q

    def _calculate_q_min_middle(self):
        """Calculates the q min value for the middle carriage through using the wavelength and two_theta_min"""
        # The min values of Middle and front are different
        self.q_min = 4 * math.pi / self.parent.parent.get_wavelength() * math.sin(self.carriages.two_theta_min / 2.0)

    def _calculate_q_min_front(self):
        """Calculates the q min value for the front carriage through using the wqx max and min values of the left and
        right panels"""
        self.q_min = min(abs(self.parent.left_panel.qx_min), abs(self.parent.left_panel.qx_max),
                         abs(self.parent.right_panel.qx_min), abs(self.parent.right_panel.qx_max))

    def _calculate_dQx_min(self):
        """Calculates the dqx min value from the q_min value without a y value using the _calculate_dq"""
        self.dqx_min = self._calculate_dq(self.q_min)

    def _calculate_dQy_min(self):
        """Calculates the dqy min value from the q_min value with a y value using the _calculate_dq"""
        self.dqy_min = self._calculate_dq(self.q_min)

    @staticmethod
    def _q_abs(qx: np.ndarray | float, qy: np.ndarray | float) -> np.ndarray | float:
        """Helper private method that square roots 2 values squared and then added together

        :param qx: The x value(s) to be squared
        :param qy: The y value(s) to be squared
        :return: The square rooted value
        :rtype: : np.ndarray | float
        """
        return np.sqrt(np.pow(qx, 2) + np.pow(qy, 2))

    def calculate_qMax(self):
        """Calculates the qmax value using the q_abs method and all the qx and y min and max values from the left and
        right panel"""
        self.q_max = max(self._q_abs(self.parent.left_panel.qx_min, self.parent.left_panel.qy_min),
                         self._q_abs(self.parent.left_panel.qx_max, self.parent.left_panel.qy_min),
                         self._q_abs(self.parent.left_panel.qx_min, self.parent.left_panel.qy_max),
                         self._q_abs(self.parent.left_panel.qx_max, self.parent.left_panel.qy_max),
                         self._q_abs(self.parent.right_panel.qx_min, self.parent.right_panel.qy_min),
                         self._q_abs(self.parent.right_panel.qx_max, self.parent.right_panel.qy_min),
                         self._q_abs(self.parent.right_panel.qx_min, self.parent.right_panel.qy_max),
                         self._q_abs(self.parent.right_panel.qx_max, self.parent.right_panel.qy_max))

    def _calculate_dQx_max(self):
        """Calculates the dqx max value from the q_max value without a y value using the _calculate_dq"""
        self.dqx_max = self._calculate_dq(self.q_max)

    def _calculate_dQy_max(self):
        """Calculates the dqy max value from the q_max value with a y value using the _calculate_dq"""
        self.dqy_max = self._calculate_dq(self.q_max)

    def calculate_d_q_values(self):
        """Calculates all the dqx and y values"""
        self._calculate_dQx_min()
        self._calculate_dQy_min()
        self._calculate_dQx_max()
        self._calculate_dQy_max()

    def calculate_all_dq(self):
        """Runs all the calculation methods necessary to calculate the dq object"""
        if self.parent.name == "front_carriage":
            self.calculate_q_min = self._calculate_q_min_front
        self.update_dq_values()
        self.calculate_q_min()
        self.calculate_qMax()
        self.calculate_d_q_values()


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
        self.x_pixel_size = 0.8
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


class VSANSConstants:
    """A class for storing and manipulating Consents for the VSANS instruments related data.

   :param Dict self.constants: The dictionary containing the constants
    """

    def __init__(self):
        """Initializes the constants objects and creates the constants parameter
        """
        self.constants = None

    def get_constants(self, preset, js_only=False):
        """Gets the constants form the required preset method

        :param str preset: The configuration name being fetched
        :param js_only: Wether to get the JS parameter only or just other parameters
        :return: The constants dictionary that is gotten
        :rtype: Dict
        """
        # Gets the constants based on the preset
        if preset == "16m":
            self.constants = self._preset_16m()
        elif preset == "11m":
            self.constants = self._preset_11m()
        elif preset == "4.5m":
            self.constants = self._preset_4_5m()
        else:
            self.constants = self._preset_19m()
        # If you only want the Js params just return the user ones
        if js_only:
            return self.constants.get("user", {})
        else:
            return self.constants

    def _initialize_presets(self) -> dict:
        user_inaccessible = dict()
        user_inaccessible["beam"] = {}
        user_inaccessible["collimation"] = {}
        user_inaccessible["middle_carriage"] = {}
        user_inaccessible["mid_left_panel"] = {}
        user_inaccessible["mid_right_panel"] = {}
        user_inaccessible["front_carriage"] = {}
        user_inaccessible["front_left_panel"] = {}
        user_inaccessible["front_right_panel"] = {}
        user_inaccessible["front_top_panel"] = {}
        user_inaccessible["front_bottom_panel"] = {}
        return user_inaccessible

    def _preset_4_5m(self):
        """Updates the user_inaccessible with the consents for the 4.5m preset

        :return:The created dictionary with sub dictionaries user_inaccessible for the js and other_constants for the
        rest of the constants
        """
        other_constants = dict()
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        other_constants["T_Frontend"] = 1.0
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible = self._initialize_presets()
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        user_inaccessible["collimation"]["guide_select"] = "9"
        user_inaccessible["collimation"]["source_aperture_js"] = "60.0"
        user_inaccessible["collimation"]["source_distance"] = 579
        user_inaccessible["collimation"]["ext_sample_aperture"] = 12.7
        user_inaccessible["collimation"]["sample_to_ap_gv"] = 22
        user_inaccessible["collimation"]["sample_to_gv"] = 11
        user_inaccessible["middle_carriage"]["ssd_input"] = 450  # SDD_middle_input
        user_inaccessible["mid_left_panel"]["offset"] = -6.0
        user_inaccessible["mid_right_panel"]["offset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 100
        user_inaccessible["front_left_panel"]["offset"] = -10.344
        user_inaccessible["front_right_panel"]["offset"] = 7.57
        user_inaccessible["front_top_panel"]["offset"] = 0
        user_inaccessible["front_bottom_panel"]["offset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_y"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_11m(self):
        """Updates the user_inaccessible with the consents for the 11m preset

        :return:The created dictionary with sub dictionaries user_inaccessible for the js and other_constants for the
        rest of the constants
        """
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        other_constants["T_Frontend"] = 1.0
        other_constants["beamstop_index"] = 4 - 1
        user_inaccessible = self._initialize_presets()
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        user_inaccessible["collimation"]["guide_select"] = "7"
        user_inaccessible["collimation"]["source_aperture_js"] = "60.0"
        user_inaccessible["collimation"]["source_distance"] = 980
        user_inaccessible["collimation"]["ext_sample_aperture"] = 12.7
        user_inaccessible["collimation"]["sample_to_ap_gv"] = 22
        user_inaccessible["collimation"]["sample_to_gv"] = 11
        user_inaccessible["middle_carriage"]["ssd_input"] = 1100  # SDD_middle_input
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        user_inaccessible["mid_left_panel"]["offset"] = -6.0
        user_inaccessible["mid_right_panel"]["offset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 230
        user_inaccessible["front_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_y"] = 0
        user_inaccessible["front_left_panel"]["offset"] = -9.32
        user_inaccessible["front_right_panel"]["offset"] = 6.82
        user_inaccessible["front_top_panel"]["offset"] = 0
        user_inaccessible["front_bottom_panel"]["offset"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_16m(self):
        """Updates the user_inaccessible with the consents for the 16m preset

        :return:The created dictionary with sub dictionaries user_inaccessible for the js and other_constants for the
        rest of the constants
        """
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        other_constants["T_Frontend"] = 1.0
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible = self._initialize_presets()
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        user_inaccessible["collimation"]["guide_select"] = "2"
        user_inaccessible["collimation"]["source_aperture_js"] = "60.0"
        user_inaccessible["collimation"]["source_distance"] = 2157
        user_inaccessible["collimation"]["ext_sample_aperture"] = 12.7
        user_inaccessible["collimation"]["sample_to_ap_gv"] = 22
        user_inaccessible["collimation"]["sample_to_gv"] = 11
        user_inaccessible["middle_carriage"]["ssd_input"] = 1600  # SDD_middle_input
        user_inaccessible["mid_left_panel"]["offset"] = -6.0
        user_inaccessible["mid_right_panel"]["offset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 350
        user_inaccessible["front_left_panel"]["offset"] = -9.627
        user_inaccessible["front_right_panel"]["offset"] = 7.0497
        user_inaccessible["front_top_panel"]["offset"] = 0
        user_inaccessible["front_bottom_panel"]["offset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_y"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_19m(self):
        """Updates the user_inaccessible with the consents for the 19m preset

        :return:The created dictionary with sub dictionaries user_inaccessible for the js and other_constants for the
        rest of the constants
        """
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        other_constants["T_Frontend"] = 1.0
        other_constants["beamstop_index"] = 2 - 1
        user_inaccessible = self._initialize_presets()
        user_inaccessible["beam"]["wavelength"] = 6  # lambda
        user_inaccessible["beam"]["dlambda"] = 0.12
        user_inaccessible["collimation"]["guide_select"] = "0"
        user_inaccessible["collimation"]["source_aperture_js"] = "30.0"  # source_aperture_str
        user_inaccessible["collimation"]["source_distance"] = 2441  # source_distance
        user_inaccessible["collimation"]["ext_sample_aperture"] = 12.7
        user_inaccessible["collimation"]["sample_to_ap_gv"] = 22
        user_inaccessible["collimation"]["sample_to_gv"] = 11
        user_inaccessible["middle_carriage"]["ssd_input"] = 1900  # SDD_middle_input
        user_inaccessible["mid_left_panel"]["offset"] = -6.0
        user_inaccessible["mid_right_panel"]["offset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 400
        user_inaccessible["front_left_panel"]["offset"] = -9.24
        user_inaccessible["front_right_panel"]["offset"] = 6.766
        user_inaccessible["front_top_panel"]["offset"] = 0
        user_inaccessible["front_bottom_panel"]["offset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["front_carriage"]["refBeamCtr_y"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}


class PlotData:
    """A class for storing and manipulating Plotting related data.

    To make the code easier to read and calculations smoother all the panel and carriage objects have been
    imported when the class was created and will be assigned on the set params

    :param VSANS self.parent: The parent VSANS object
    :param str self.name: The name of the class
    :param MiddleCarriage self.middle_carriage: The middle carriage object from the Parent class
    :param VerticalPanel self.mid_left_panel: The left panel object from the parent.middleCarriage class
    :param VerticalPanel self.mid_right_panel: The right panel object from the parent.middleCarriage class
    :param HorizontalPanel self.mid_top_panel: The top panel object from the parent.middleCarriage class
    :param HorizontalPanel self.mid_bottom_panel: The bottom panel object from the parent.middleCarriage class
    :param FrontCarriage self.front_carriage: The front carriage object from the parent class
    :param VerticalPanel self.front_left_panel: The left panel object from the parent.frontCarriage class
    :param VerticalPanel self.front_right_panel: The right panel object from the parent.frontCarriage class
    :param HorizontalPanel self.front_top_panel: The top panel object from the parent.frontCarriage class
    :param HorizontalPanel self.front_bottom_panel: The bottom panel object from the parent.frontCarriage class
    :param Array self.all_detectors: An array that contains all the detectors to be looped through easily
    :param Float self.lambda_val: The wavelength value from the parent.beam.wavelength value
    :param Array self.default_mask: An array that contains the default mask
    :param Boolean self.k_bctr_cm: A boolean value that is used in the calculations
    """

    def __init__(self, parent, params, name="PlotData"):
        """ Creates object parameters for PlotData class and runs set params method

        Sets object parameters self.middle_carriage, self.mid_left_panel, self.mid_right_panel, self.mid_top_panel,
        self.mid_bottom_panel, self.front_carriage, self.front_left_panel, self.front_right_panel, self.front_top_panel,
         self.front_bottom_panel, self.all_detectors, self.lambda_val, self.default_mask, and self.k_bctr_cm

        :param VSANS parent: The VSANS instance this PlotData is a part of
        :param dict params: A dictionary mapping <param_name>: <value>
        :param str name: The name of the class
        :return: None as it just sets the parameters
        :rtype: None
        """
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
        self.intensity = 0.0

        set_params(instance=self, params=params)

    def run_plot_data(self):
        """Runs all the calculation methods nessasary to calculate the plots object"""
        # Initialize the space and all the variables
        self.initialize_space()

        # Generates default mask
        self.generate_default_mask()

        # Calculates all the data
        self.calculate_all_detectors()

    def initialize_space(self):
        """Creates the all detectors array based on all the panel objects that exist in this panel and then loops
        through that array, creating all of the detectors"""
        # All the other variables are set in their classes as they are constants
        # Creates an object that contains all the detector objects and can be lopped through
        self.all_detectors = [self.mid_left_panel, self.mid_right_panel, self.mid_top_panel, self.mid_bottom_panel,
                              self.front_left_panel, self.front_right_panel, self.front_top_panel,
                              self.front_bottom_panel]
        # Creates each detector in the subclass
        for panel in self.all_detectors:
            panel.create_detector_array()

    def generate_default_mask(self):
        """Generates the default mask based on some constants and then calls the create default mask method"""

        # Overall Default Mask
        inner_array = np.concatenate((np.ones(39), np.zeros(1496), np.ones(121)))
        self.default_mask = np.concatenate(
            (np.zeros((191, 1656)), np.tile(inner_array, (478, 1)), np.zeros((11, 1656))))

        # Generate the default mask for each individual detector
        for panel in self.all_detectors:
            panel.create_default_mask()

    def calculate_all_detectors(self):
        """Calculation method to calculate the 1 and 2d plots"""
        # calculates Q for each panel and fills 2D panels with model data then plots the 2D panel
        # self.plot_back_panel() # We are not worrying about the back Panel
        self.plot_all_panels()

        # generate a proper mask based on hard + soft shadowing
        self.reset_mask()
        for panel in self.all_detectors:
            panel.draw_mask()

        self.calculate_beam_intensity()

        # Fill in the Qmin and Qmax values, based on Q_Tot for the 2D panels ( not including mask)
        # self.v_q_min_max_back() # We are not worrying about the back Panel
        # self.v_q_min_max_middle()
        # self.v_q_min_max_front()

        # Calculate beam diameter and beamstop size
        # V_BeamDiamDisplay("maximum", "MR") // TODO - - hard - wired here for the Middle carriage ( and in the
        #  SetVar label)
        # V_BeamStopDiamDisplay("MR")

        # self.beam_biam_display()
        # self.beam_stop_diam_display()
        # Calculate the "real" QMin with the beamstop
        # V_QMin_withBeamStop("MR") // TODO - - hard - wired
        #
        # self.calculate_q_min_beam_stop()
        #
        # The 1 D I(q) - get the values, re - do the calc at the end
        # popStr
        # collimationStr = "pinhole"
        # ControlInfo / W = VCALC
        # popup_b
        # popStr = S_Value
        # V_QBinAllPanels_Circular("VCALC", V_BinTypeStr2Num(popStr), collimationStr)
        # self.bin_all_panels_circular()
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
        # self.iq_beam_stop_shadow()

    # Helper functions for the sub functions of run_plot_data
    # Start calculate panel function
    def plot_all_panels(self):
        """Runs the plot calculations and fills with model data on all panels

        fPlotMiddlePanels in IgorPro"""
        # calculate Qtot, qxqyqz arrays from geometry
        for panel in self.all_detectors:
            panel.plot_panel()
            panel.fill_panel_w_ones()

    def reset_mask(self):
        """Resets the panel.data array to zeros to allow for better calculations"""
        for panel in self.all_detectors:
            panel.data = np.zeros((len(panel.detector_array), len(panel.detector_array[0])))

    # DEVNote- Functions created as they were used in igorPro but I did not have time to implement
    def calculate_beam_intensity(self):
        """Calculate the beam intensity at the closest detector"""
        lambda_t = 6.20
        phi_0 = 1.82e13
        wavelength = self.parent.get_wavelength()
        t_special = 1  # Placeholder for future use
        t_total = self.parent.collimation.t_filter * self.parent.collimation.t_guide * t_special
        a1_area = math.pi * math.pow(self.parent.collimation.source_aperture / 2., 2)
        a2_area = math.pi * math.pow(self.parent.collimation.sample_aperture / 2., 2)
        d2_phi = phi_0 / (2 * math.pi)
        d2_phi *= math.exp(4 * math.log(lambda_t / wavelength))
        d2_phi *= math.exp(-1 * (lambda_t * lambda_t / wavelength / wavelength ))
        solid_angle = a1_area/ math.pow(self.parent.get_l_1(), 2)
        self.intensity = a2_area * d2_phi * self.parent.beam.dlambda * solid_angle * t_total
    #
    # def v_q_min_max_middle(self):
    #     pass
    #
    # def v_q_min_max_front(self):
    #     pass
    #
    # def beam_biam_display(self):
    #     pass
    #
    # def beam_stop_diam_display(self):
    #     pass
    #
    # def calculate_q_min_beam_stop(self):
    #     pass
    #
    # def iq_beam_stop_shadow(self):
    #     pass
