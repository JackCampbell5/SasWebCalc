import math

import numpy as np

from .InstrumentBase import Instrument
from ..instrument import CALC_TYPE, set_params
from ..instrument import Collimation as BaseCollimation
from ..instrumentJSParams import *
from ..components.Panels import AllCarriage, MiddleCarriage, FrontCarriage


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
        self.panels = []
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
        self.panels = [self.middle_carriage.top_panel, self.middle_carriage.bottom_panel,
                       self.middle_carriage.left_panel, self.middle_carriage.right_panel,
                       self.front_carriage.top_panel, self.front_carriage.bottom_panel,
                       self.front_carriage.left_panel, self.front_carriage.right_panel]

        for panel in self.panels:
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
        for index in range(len(self.panels)):
            self.calculate_slicer(index)
        # Calculate all the Plots
        user_inaccessible = _create_vsans_dict(is_named=False)
        user_inaccessible["beam"]["wavelength"] = self.beam.wavelength
        user_inaccessible["beam"]["dlambda"] = self.beam.dlambda
        user_inaccessible["beam"]["frontend_trans"] = self.beam.frontend_trans
        user_inaccessible["beam"]["flux"] = self.beam.flux
        user_inaccessible["beam"]["beam_current"] = self.beam.beam_current
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
            python_return["data"][i]["name"] = self.panels[i].short_name if i < len(self.panels) else f"Panel {i}"
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

    @staticmethod
    def vcalc_pixel_positions(panel) -> tuple[np.ndarray, np.ndarray, float, float]:
        """Real-space pixel positions of a panel relative to the beam center, as calculated by VCALC in Igor.

        Port of VC_MakeRealDistXYWaves -> V_NonLinearCorrection (with the "perfect" tube calibration) and of the
        kBCTR_CM beam center calculation in VC_CalculateQFrontPanels / VC_CalculateQMiddlePanels.

        * The panel offset (VCALC "translation") is the position [cm] of the panel's inner edge relative to the beam:
          negative to the left/below the beam, positive to the right/above it. Each panel's tubes start half the
          panel gap away from that edge.
        * Vertical (L/R) panels: x is set by the 48 tubes (8.4 mm wide), y by the position along the tube
          (-521 mm + 8.14 mm * pixel). Horizontal (T/B) panels: y is set by the tubes, x by -266 mm + 4.16 mm * pixel.

        :param panel: A VerticalPanel or HorizontalPanel
        :return: x positions [cm] (one per pixel column), y positions [cm] (one per pixel row), and the beam center
            x, y [mm] in the panel's real-distance coordinates
        """
        detector = panel.detectors
        name = panel.short_name
        side = name[1]
        tube_width = 8.4  # [mm]
        gap = detector.panel_gap * 10.0  # [mm]
        sep = float(panel.offset or 0.0)  # [cm]
        offset = sep * 10.0  # [mm]
        n_x, n_y = int(detector.x_dim), int(detector.y_dim)
        p = np.arange(n_x, dtype=float)
        q = np.arange(n_y, dtype=float)
        pix_x, pix_y = panel.x_pixel_size, panel.y_pixel_size  # [cm]
        if not panel.horizontal_orientation:
            if side == "L":
                real_x = offset - (n_x - p - 0.5) * tube_width - gap / 2
            else:
                real_x = tube_width * (p + 0.5) + offset + gap / 2
            real_y = -521.0 + 8.14 * q
            # Beam center in pixels, then converted to cm (kBCTR_CM)
            if side == "L":
                x_ctr = real_x[n_x - 1] / 10 + ((n_x - sep / pix_x) - n_x - 1) * pix_x
            else:
                x_ctr = real_x[0] / 10 + (-(sep / pix_x) - 1) * pix_x
            y_ctr = real_y[int(n_y / 2)] / 10
        else:
            if side == "T":
                real_y = tube_width * (q + 0.5) + offset + gap / 2
            else:
                real_y = offset - (n_y - q - 0.5) * tube_width - gap / 2
            real_x = -266.0 + 4.16 * p
            # VCALC uses half the translation for the front T/B beam centers, but the full value for the middle
            sep_ctr = sep / 2 if name[0] == "F" else sep
            x_ctr = real_x[int(n_x / 2)] / 10
            if side == "T":
                y_ctr = real_y[0] / 10 + (-(sep_ctr / pix_y) - 1) * pix_y
            else:
                y_ctr = real_y[n_y - 1] / 10 + ((n_y - sep_ctr / pix_y) - n_y - 1) * pix_y
        # VCALC passes these centers (computed in cm) straight to V_CalcQval, which subtracts them from the mm
        # real-distance waves. The same is done here so the Q values match VCALC.
        # The reference beam center (cm) shifts the beam relative to the panels.
        x_ctr_mm = x_ctr + panel.parent.refBeamCtr_x * 10.0
        y_ctr_mm = y_ctr + panel.parent.refBeamCtr_y * 10.0
        x_positions = (real_x - x_ctr_mm) / 10.0
        y_positions = (real_y - y_ctr_mm) / 10.0
        return x_positions, y_positions, x_ctr_mm, y_ctr_mm

    def calculate_slicer(self, index=0):
        """Creates the slicer for a single VSANS panel.

        The generic Instrument.calculate_slicer() reads pixel size and beam center from a base Detector, which VSANS
        does not populate, so the panel geometry is passed explicitly here. Pixel positions relative to the beam are
        calculated as VCALC does (see vcalc_pixel_positions). All lengths are in cm.

        :param int index: The index of the panel in self.panels
        """
        panel = self.panels[index]
        detector = panel.detectors
        carriage = panel.parent
        x_positions, y_positions, _, _ = self.vcalc_pixel_positions(panel)
        # Pixel spacing from the real-distance waves
        pixel_size_x = float(np.mean(np.diff(x_positions)))
        pixel_size_y = float(np.mean(np.diff(y_positions)))

        slicer_params = dict(self.slicer_params) if self.slicer_params else {}
        slicer_params.update({
            "x_pixels": detector.x_dim,
            "y_pixels": detector.y_dim,
            "x_positions": x_positions,
            "y_positions": y_positions,
            "pixel_size_x": pixel_size_x,
            "pixel_size_y": pixel_size_y,
            "pixel_size": (pixel_size_x + pixel_size_y) / 2.0,
            # VCALC uses the pixel size as the detector resolution (V_getResolution: DDet = pixel size x)
            "detector_resolution": panel.x_pixel_size,
            "lambda_val": self.get_wavelength(),
            "lambda_width": self.get_wavelength_spread(),  # dlambda is fractional, as the slicer expects
            "lens": False,
            "source_aperture": self.get_source_aperture_size(),  # radius, cm
            "sample_aperture": self.get_sample_aperture_size(),  # radius, cm
            # beamstop_required is in inches. The beam stop sits on the middle carriage, so it doesn't shadow the
            # front carriage panels.
            "beam_stop_size": 0.0 if carriage is self.front_carriage else self.get_beam_stop_diameter() * 2.54,
            "SSD": self.get_source_to_sample_aperture_distance(),
            # Sample to detector (VC_getSDD: gate valve to detector + sample to gate valve) and sample aperture to
            # detector, including the 41 cm setback of the T/B panels (VCALC_getTopBottomSDDSetback)
            "SDD": carriage.ssd + detector.setback,
            "detector_distance": carriage.l_2 + detector.setback,
        })
        self.create_slicer(index, slicer_params)

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
