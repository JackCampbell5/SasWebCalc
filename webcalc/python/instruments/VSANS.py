from ..instrumentJSParams import *
from typing import Dict, List, Union
import numpy as np
from ..instrument import set_params
import math

Number = Union[float, int]


def _create_vsans_dict(name=True, additional=False):
    """Creates the sub dictionary necessary for the VSANS instrument to work properly and returns the all in 1
    dictionary

    :param Boolean name:
    :param Boolean additional:
    :return:
    """
    vsans_dict = {}
    vsans_dict["presets"] = {"name": "Presets"} if name else {}
    vsans_dict["beam"] = {"name": "Beam"} if name else {}
    vsans_dict["collimation"] = {"name": "Collimation"} if name else {}
    vsans_dict["middle_carriage"] = {"name": "Middle Carriage"} if name else {}
    vsans_dict["mid_left_panel"] = {"name": "Middle Carriage Left Panel"} if name else {}
    vsans_dict["mid_right_panel"] = {"name": "Middle Carriage Right Panel"} if name else {}
    vsans_dict["mid_top_panel"] = {"name": "Middle Carriage Top Panel"} if name else {}
    vsans_dict["mid_bottom_panel"] = {"name": "Middle Carriage Bottom Panel"} if name else {}
    vsans_dict["front_carriage"] = {"name": "Front Carriage"} if name else {}
    vsans_dict["front_left_panel"] = {"name": "Front Carriage Left Panel"} if name else {}
    vsans_dict["front_right_panel"] = {"name": "Front Carriage Right Panel"} if name else {}
    vsans_dict["front_top_panel"] = {"name": "Front Carriage Top Panel"} if name else {}
    vsans_dict["front_bottom_panel"] = {"name": "Front Carriage Bottom Panel"} if name else {}
    vsans_dict["options"] = {}
    if additional:
        vsans_dict["all_carriage"] = {}
        vsans_dict["mid_dq_values"] = {}
        vsans_dict["front_dq_values"] = {}
    return vsans_dict


class VSANS:
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

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the instrument classes constructor

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
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
        self.constants = VSANS_Constants().get_constants(self.preset, _create_vsans_dict(name=False))  # TODO Look at
        # if this is necessary
        # Super is the Instrument class
        params = params["instrument_params"]
        self.load_params(params)

    def load_params(self, old_params):
        """A method that loads the constants of the VSANS Instrument

        :param dict old_params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("VSANS Load Params")
        params = self.param_restructure(old_params)

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "VSANS.ncnr.nist.gov"
        params["beam"]["frontend_trans_options"] = {"0.02": 0.5, "0.12": 1.0, "0.4": 0.7}
        params["beam"]["lambda_T"] = self.constants.get("lambda_T", 6.2)
        params["beam"]["phi_0"] = self.constants.get("phi_0", 1.82e13)
        params["front_carriage"]["front_lr_w"] = 40.3
        params["front_carriage"]["front_lr_h"] = 100.0
        params["front_carriage"]["front_tb_w"] = 50.0
        params["front_carriage"]["front_tb_h"] = 40.3
        params["front_carriage"]["front_ssd_setback"] = 41.0
        params["front_left_panel"]["beam_center_x"] = 55
        params["front_left_panel"]["beam_center_y"] = 64
        params["front_right_panel"]["beam_center_x"] = -8
        params["front_right_panel"]["beam_center_y"] = 64
        params["front_top_panel"]["beam_center_x"] = 64
        params["front_top_panel"]["beam_center_y"] = -8
        params["front_bottom_panel"]["beam_center_x"] = 64
        params["front_bottom_panel"]["beam_center_y"] = 55
        # Middle Carriage constants
        params["middle_carriage"]["middle_lr_w"] = 40.3
        params["middle_carriage"]["middle_lr_h"] = 100.0
        params["middle_carriage"]["middle_tb_w"] = 50.0
        params["middle_carriage"]["middle_tb_h"] = 40.3
        params["middle_carriage"]["middle_ssd_setback"] = 41.0
        params["mid_left_panel"]["beam_center_x"] = 55
        params["mid_left_panel"]["beam_center_y"] = 64
        params["mid_right_panel"]["beam_center_x"] = -8
        params["mid_right_panel"]["beam_center_y"] = 64
        params["mid_top_panel"]["beam_center_x"] = 64
        params["mid_top_panel"]["beam_center_y"] = -8
        params["mid_bottom_panel"]["beam_center_x"] = 64
        params["mid_bottom_panel"]["beam_center_y"] = 55

        self.load_objects(params)

    @staticmethod
    def param_restructure(old_params):
        """ A method that takes the list of params from the Javascript and assigns it to a dictionary allowing the python to assign variables to objects

        :param dict old_params: A dictionary of the values gotten from the js
        :return: An dictionary of the params that has been restructured correctly
        :rtype: Dict
        """

        def _param_get_helper(name="", category="", key="default", default_value=None, division=1):
            """ Checks if a value exists at a certain key and if not sets the value to none ot be removed later

            :param str name: the dictionary of parameters to get the value from
            :param str key: The name of the key you want the value of
            :param default_value: The default value if none exists at that location in the params dictionary
            :param int division: The number to device by if necessary for debuting
            :return: The value at the keys position in the dictionary or None
            :rtype: str, None
            """
            # TODO get default values if possible from constants.py
            params = old_params.get(category, {}).get(name, {})
            try:
                result = params.get(key, default_value)
                if division != 1:
                    result = result / 100
            except AttributeError:
                return None
            # If it is blank make the value none
            if result == "":
                return default_value
            return result

        params = _create_vsans_dict(name=False, additional=True)
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
        params["mid_left_panel"]["lateral_offset"] = _param_get_helper(name="lateral_offset", category="mid_left_panel",
                                                                       default_value=-6)
        params["mid_left_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="mid_left_panel",
                                                               default_value=0.003822)
        params["mid_left_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="mid_left_panel",
                                                               default_value=-0.02545)
        params["mid_right_panel"]["lateral_offset"] = _param_get_helper(name="lateral_offset",
                                                                        category="mid_right_panel", default_value=-5.5)
        params["mid_right_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="mid_right_panel",
                                                                default_value=-0.002622)
        params["mid_right_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="mid_right_panel",
                                                                default_value=0.01901)
        params["mid_right_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_right_panel",
                                                                default_value=0.02854)
        params["mid_right_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_right_panel",
                                                                default_value=0.02809)
        params["mid_top_panel"]["verticalOffset"] = _param_get_helper(name="verticalOffset", category="mid_top_panel",
                                                                      default_value=0)
        params["mid_top_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_top_panel", default_value=0)
        params["mid_top_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_top_panel", default_value=0)
        params["mid_bottom_panel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
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
        params["front_left_panel"]["lateral_offset"] = _param_get_helper(name="lateral_offset",
                                                                         category="front_left_panel",
                                                                         default_value=-9.24)
        params["front_left_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="front_left_panel",
                                                                 default_value=-0.02538)
        params["front_left_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="front_left_panel",
                                                                 default_value=-0.1253)
        params["front_left_panel"]["match_button"] = _param_get_helper(name="match_button", category="front_left_panel",
                                                                       default_value=False)
        params["front_right_panel"]["lateral_offset"] = _param_get_helper(name="lateral_offset",
                                                                          category="front_right_panel",
                                                                          default_value=6.766)
        params["front_right_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="front_right_panel",
                                                                  default_value=0.01875)
        params["front_right_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="front_right_panel",
                                                                  default_value=0.1188)
        params["front_right_panel"]["match_button"] = _param_get_helper(name="match_button",
                                                                        category="front_right_panel",
                                                                        default_value=False)
        params["front_top_panel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
                                                                        category="front_top_panel", default_value=0)
        params["front_top_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="front_top_panel",
                                                                default_value=0.001147)
        params["front_top_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="front_top_panel",
                                                                default_value=0.09234)
        params["front_top_panel"]["match_button"] = _param_get_helper(name="match_button", category="front_top_panel",
                                                                      default_value=False)
        params["front_bottom_panel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
                                                                           category="front_bottom_panel",
                                                                           default_value=0)
        params["front_bottom_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="front_bottom_panel",
                                                                   default_value=-0.003139)
        params["front_bottom_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="front_bottom_panel",
                                                                   default_value=-0.09432)
        params["front_bottom_panel"]["match_button"] = _param_get_helper(name="match_button",
                                                                         category="front_bottom_panel",
                                                                         default_value=False)
        return params

    def load_objects(self, params):
        """A function that creates the objects necessary for the calculations

        Create objects beam_stops, detectors, collimation, and wavelength

        :param dict params: A dictionary of parameters to send to the initialization of the objects
        :return: Nothing as it just sets up all the objects
        :rtype: None
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
        """Runs the calculate method of all the objects created in load objects

        :return: Nothing as it just runs methods
        :rtype: None
        """
        self.beam.calculate_beam()
        self.collimation.calculate_collimation()
        self.all_carriage.calculate_all_Carriage()
        self.middle_carriage.calculate_middleCarriage()
        self.front_carriage.calculate_frontCarriage()

    def calculate_plots(self):
        """A method that  takes in all the params from the other classes needed to calculate the plot data and passes it
        as a parameter to the innit statement of the PLotData class

        :return: None as it just creates a dictionary and then runs functions
        :rtype: None
        """
        plot_params = {}
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
    def get_wavelength(self):
        """Gets the wavelength parameter from the beam object

        :return: The values of the wavelength parameter
        :rtype: Float
        """
        return self.beam.wavelength

    def get_l_1(self):
        """Gets the l_1 parameter from the collimation object

        :return: The values of the l_1 parameter
        :rtype: Float
        """
        return self.collimation.l_1

    def get_l_2(self):
        """Gets the l_2 parameter from the middle carriage object

        :return: The values of the l_2 parameter
        :rtype: Float
        """
        return self.middle_carriage.l_2

    def get_source_aperture(self):
        """Gets the source aperture parameter from the collimation object

        :return: The values of the source aperture parameter
        :rtype: Float
        """
        return self.collimation.source_aperture

    def get_sample_aperture(self):
        """Gets the sample aperture parameter from the collimation object

        :return: The values of the sample aperture parameter
        :rtype: Float
        """
        return self.collimation.sample_aperture

    # Get methods before here

    def sas_calc(self) -> Dict[str, Union[Number, str, List[Union[Number, str]]]]:
        """ The main function that runs all the calculation though the calculate objects and calculate plot methods and
        returns the results

        Makes a user inaccessible sub dictionary witch contains the results to be sent back to the instrument JS

        :return: A dictionary of the calculation results
        :rtype: Dict
        """
        # Calculate all the objects
        self.calculate_objects()
        self.calculate_plots()
        # Calculate all the Plots
        user_inaccessible = _create_vsans_dict(name=False)
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
        user_inaccessible["mid_left_panel"]["lateral_offset"] = self.middle_carriage.left_panel.lateral_offset
        user_inaccessible["mid_left_panel"]["qx_max"] = self.middle_carriage.left_panel.qx_max
        user_inaccessible["mid_left_panel"]["qx_min"] = self.middle_carriage.left_panel.qx_min
        user_inaccessible["mid_right_panel"]["lateral_offset"] = self.middle_carriage.right_panel.lateral_offset
        user_inaccessible["mid_right_panel"]["qx_min"] = self.middle_carriage.right_panel.qx_min
        user_inaccessible["mid_right_panel"]["qx_max"] = self.middle_carriage.right_panel.qx_max
        user_inaccessible["mid_right_panel"]["qy_min"] = self.middle_carriage.right_panel.qy_min
        user_inaccessible["mid_right_panel"]["qy_max"] = self.middle_carriage.right_panel.qy_max
        user_inaccessible["mid_top_panel"]["verticalOffset"] = self.middle_carriage.top_panel.verticalOffset
        user_inaccessible["mid_top_panel"]["qy_min"] = self.middle_carriage.top_panel.qy_min
        user_inaccessible["mid_top_panel"]["qy_max"] = self.middle_carriage.top_panel.qy_max
        user_inaccessible["mid_bottom_panel"]["verticalOffset"] = self.middle_carriage.bottom_panel.verticalOffset
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
        user_inaccessible["front_left_panel"]["lateral_offset"] = self.front_carriage.left_panel.lateral_offset
        user_inaccessible["front_left_panel"]["qx_max"] = self.front_carriage.left_panel.qx_max
        user_inaccessible["front_left_panel"]["qx_min"] = self.front_carriage.left_panel.qx_min
        user_inaccessible["front_left_panel"]["match_button"] = self.front_carriage.left_panel.match_button
        user_inaccessible["front_right_panel"]["lateral_offset"] = self.front_carriage.right_panel.lateral_offset
        user_inaccessible["front_right_panel"]["qx_min"] = self.front_carriage.right_panel.qx_min
        user_inaccessible["front_right_panel"]["qx_max"] = self.front_carriage.right_panel.qx_max
        user_inaccessible["front_right_panel"]["match_button"] = self.front_carriage.right_panel.match_button
        user_inaccessible["front_top_panel"]["verticalOffset"] = self.front_carriage.top_panel.verticalOffset
        user_inaccessible["front_top_panel"]["qy_min"] = self.front_carriage.top_panel.qy_min
        user_inaccessible["front_top_panel"]["qy_max"] = self.front_carriage.top_panel.qy_max
        user_inaccessible["front_top_panel"]["match_button"] = self.front_carriage.top_panel.match_button
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = self.front_carriage.bottom_panel.verticalOffset
        user_inaccessible["front_bottom_panel"]["qy_max"] = self.front_carriage.bottom_panel.qy_max
        user_inaccessible["front_bottom_panel"]["qy_min"] = self.front_carriage.bottom_panel.qy_min
        user_inaccessible["front_bottom_panel"]["match_button"] = self.front_carriage.bottom_panel.match_button
        python_return = {"user_inaccessible": user_inaccessible}
        if self.options is not {}:
            python_return['options'] = self.options
        return python_return

    @staticmethod
    def update_values(info):
        """The update values method for the VSANS instrument which happens when a js value is changed and other
        values need to be updated because of it

        :param str info: What is being sent by the server
        :return: A dictionary of the values to be changed
        :rtype: Dict
        """
        type_info = info[:info.find('@')]
        rest_info = info[info.find('@') + 1:]
        if type_info == "preset":
            return VSANS.preset_change(rest_info)
        elif type_info == "guideUpdate":
            source_aperture_js = rest_info[:rest_info.find('+')]
            guide_select = rest_info[rest_info.find('+') + 1:]
            return VSANS.update_source_aperture(source_aperture_js=source_aperture_js, guide_select=guide_select)

    @staticmethod
    def preset_change(preset):
        """If the value being updated is a preset then create a constants object and get the constants from it

        :param str preset: The preset which was decoded by the update values funtion
        :return: A dictionary of the values to be updated
        :rtype: Dict
        """
        constants = VSANS_Constants()
        results = constants.get_constants(preset, _create_vsans_dict(name=False), True)
        results = VSANS.update_source_aperture_with_data(results)
        return check_params(params=results)

    @staticmethod
    def update_source_aperture_with_data(results):
        """Updates the value of the source aperture based on the guide number and current value gotten from an array
        of params by calling the update_source_aperture method

        :param dict results: A dictionary of params that contains the source_aperture_js and guide_select params
        :return: The results dictionary but with the source aperture updated
        :rtype: Dict
        """
        # Update the number of guides to be correct
        source_aperture_js = results["collimation"]["source_aperture_js"]
        guide_select = results["collimation"]["guide_select"]
        return VSANS.update_source_aperture(results=results, source_aperture_js=source_aperture_js,
                                            guide_select=guide_select)

    @staticmethod
    def update_source_aperture(results=None, source_aperture_js='0.0', guide_select='0'):
        """Updates the value of the source aperture based on the number of guides

        :param dict results: A dictionary to output the results
        :param str source_aperture_js: The string value of the source aperture
        :param str guide_select: The string value of the number of guides
        :return: The results dictionary
        :rtype: Dict
        """
        if results is None: results = {"collimation": {}, "options": {}}
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
        results["options"]["collimation+ source_aperture_js"] = {"type": "options", "set_to": valid_ops}
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
        params["beam"]["i_sub_zero"] = create_number_output(name="I0", unit="1/s/cm^2", default=8.332e+4)
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
        params["mid_left_panel"]["lateral_offset"] = create_number_input(name="Lateral Offset", unit="cm", default=-6)
        params["mid_left_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.003822)
        params["mid_left_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.02545)
        params["mid_right_panel"]["lateral_offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                          default=-5.5)
        params["mid_right_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.002622)
        params["mid_right_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.01901)
        params["mid_right_panel"]["qy_min"] = create_number_output(name="Q_bottom", unit="1/Å", default=-0.02854)
        params["mid_right_panel"]["qy_max"] = create_number_output(name="Qtop", unit="1/Å", default=0.02809)
        params["mid_top_panel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["mid_top_panel"]["qy_min"] = create_number_output(name="Qbottom", unit="1/Å", default=0.0)
        params["mid_top_panel"]["qy_max"] = create_number_output(name="q_top", unit="1/Å", default=0.0)
        params["mid_bottom_panel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
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
        params["front_left_panel"]["lateral_offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                           default=-9.24)
        params["front_left_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.02538)
        params["front_left_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.1253)
        params["front_left_panel"]["match_button"] = create_checkbox(name="Match to left edge of ML?", default=False)
        params["front_right_panel"]["lateral_offset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                            default=6.766)
        params["front_right_panel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=0.01875)
        params["front_right_panel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.1188)
        params["front_right_panel"]["match_button"] = create_checkbox(name="Match right edge to of MR", default=False)
        params["front_top_panel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["front_top_panel"]["qy_min"] = create_number_output(name="Qbottom", unit="1/Å", default=0.001147)
        params["front_top_panel"]["qy_max"] = create_number_output(name="q_top", unit="1/Å", default=0.09234)
        params["front_top_panel"]["match_button"] = create_checkbox(name="Match Top Edge to MR", default=False)
        params["front_bottom_panel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm",
                                                                             default=0)
        params["front_bottom_panel"]["qy_max"] = create_number_output(name="Q_Top", unit="1/Å", default=-0.003139)
        params["front_bottom_panel"]["qy_min"] = create_number_output(name="Q_Bottom", unit="1/Å", default=-0.09432)
        params["front_bottom_panel"]["match_button"] = create_checkbox(name="Match Bottom Edge of MR", default=False)

        params = check_params(params=params)
        return params


class Beam:
    """

    """
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
                math.pow((self.imported_l_1 + self.parent.get_l_2()), 2) - (
                self.imported_l_1 + self.parent.get_l_2()) * self.imported_l_1)

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
        beam_size_geometric = self.parent.get_source_aperture() * self.parent.get_l_2() / self.imported_l_1 + self.parent.get_sample_aperture() * (
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


class VSANS_Constants:
    def __init__(self):
        self.constants = None

    def get_constants(self, preset, VSANS_dict, js_only=False):
        # Gets the constants based on the preset
        if preset == "16m":
            self.constants = self._preset_16m(VSANS_dict)
        elif preset == "11m":
            self.constants = self._preset_11m(VSANS_dict)
        elif preset == "4.5m":
            self.constants = self._preset_4_5m(VSANS_dict)
        else:
            self.constants = self._preset_19m(VSANS_dict)
        # If you only want the Js params just return the user ones
        if js_only:
            return self.constants.get("user", {})
        else:
            return self.constants.get("other", {})

    def _preset_4_5m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "9"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 579
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 450  # SDD_middle_input
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 100
        user_inaccessible["front_left_panel"]["lateralOffset"] = -10.344
        user_inaccessible["front_right_panel"]["lateralOffset"] = 7.57
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_11m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "7"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 980
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1100  # SDD_middle_input
        other_constants["beamstop_index"] = 4 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 230
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.32
        user_inaccessible["front_right_panel"]["lateralOffset"] = 6.82
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_16m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "2"
        user_inaccessible["collimation"]["sourceAperture_js"] = "60.0"
        user_inaccessible["collimation"]["sourceDistance"] = 2157
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1600  # SDD_middle_input
        other_constants["beamstop_index"] = 3 - 1
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 350
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.627
        user_inaccessible["front_right_panel"]["lateralOffset"] = 7.0497
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}

    def _preset_19m(self, user_inaccessible):
        other_constants = {}
        other_constants["phi_0"] = 1.82e13
        other_constants["lambda_T"] = 6.2
        user_inaccessible["beam"]["wavelength"] = 6  # lambda
        user_inaccessible["beam"]["dlambda"] = 0.12
        other_constants["T_Frontend"] = 1.0
        user_inaccessible["collimation"]["guide_select"] = "0"
        user_inaccessible["collimation"]["sourceAperture_js"] = "30.0"  # source_aperture_str
        user_inaccessible["collimation"]["sourceDistance"] = 2441  # source_distance
        user_inaccessible["collimation"]["extSampleAperture"] = 12.7
        user_inaccessible["collimation"]["sampleToApGv"] = 22
        user_inaccessible["collimation"]["sampleToGv"] = 11
        user_inaccessible["middle_carriage"]["ssdInput"] = 1900  # SDD_middle_input
        other_constants["beamstop_index"] = 2 - 1
        user_inaccessible["mid_left_panel"]["lateralOffset"] = -6.0
        user_inaccessible["mid_right_panel"]["lateralOffset"] = -5.5
        user_inaccessible["front_carriage"]["ssd_input"] = 400
        user_inaccessible["front_left_panel"]["lateralOffset"] = -9.24
        user_inaccessible["front_right_panel"]["lateralOffset"] = 6.766
        user_inaccessible["front_top_panel"]["verticalOffset"] = 0
        user_inaccessible["front_bottom_panel"]["verticalOffset"] = 0
        user_inaccessible["front_carriage"]["refBeamCtrX"] = 0
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_x"] = 0
        user_inaccessible["middle_carriage"]["refBeamCtr_y"] = 0
        return {"user": user_inaccessible, "other": other_constants}


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
