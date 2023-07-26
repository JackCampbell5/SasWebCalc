from ..instrument import Instrument
from ..instrumentJSParams import *
from typing import Dict, List, Union
from ..instrumentVSANS import *
from ..constants import VSANS_Constants

Number = Union[float, int]


def _create_vsans_dict(name=True, additional=False):
    vsans_dict = {}
    vsans_dict["presets"] = {"name": "Presets"} if name else {}
    vsans_dict["beam"] = {"name": "Beam"} if name else {}
    vsans_dict["collimation"] = {"name": "Collimation"} if name else {}
    vsans_dict["middle_carriage"] = {"name": "Middle Carriage"} if name else {}
    vsans_dict["mid_left_panel"] = {"name": "Middle Carriage Left Panel"} if name else {}
    vsans_dict["mid_right_panel"] = {"name": "Middle Carriage Right Panel"} if name else {}
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


class VSANS():
    """ A class to manipulate NG7SANS as a subclass of the instrument class

    :param  self.name: The name of the instrument
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
        self.constants = VSANS_Constants().get_constants(self.preset, _create_vsans_dict(name=False))
        # Super is the Instrument class
        params = params["instrument_params"]
        self.load_params(params)

    def load_params(self, params):
        """A method that loads the constants of the VSANS Instrument

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("VSANS Load Params")
        params = self.param_restructure(params)

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "VSANS.ncnr.nist.gov"
        params["beam"]["frontend_trans_options"] = {"0.02": 0.5, "0.12": 1.0, "0.4": 0.7}
        params["beam"]["lambda_T"] = self.constants.get("lambda_T", 6.2)
        params["beam"]["phi_0"] = self.constants.get("phi_0", 1.82e13)

        self.load_objects(params)

    def param_restructure(self, old_params):
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
        params["all_carriage"]["l_2"] = _param_get_helper(name="l_2", category="middle_carriage", default_value=1922)
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
                                                                        category="mid_right_panel",
                                                                     default_value=-5.5)
        params["mid_right_panel"]["qx_min"] = _param_get_helper(name="qx_min", category="mid_right_panel",
                                                              default_value=-0.002622)
        params["mid_right_panel"]["qx_max"] = _param_get_helper(name="qx_max", category="mid_right_panel",
                                                              default_value=0.01901)
        params["mid_right_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="mid_right_panel",
                                                              default_value=0.02854)
        params["mid_right_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="mid_right_panel",
                                                              default_value=0.02809)
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
                                                                        category="front_top_panel",
                                                                      default_value=0)
        params["front_top_panel"]["qy_min"] = _param_get_helper(name="qy_min", category="front_top_panel",
                                                              default_value=0.001147)
        params["front_top_panel"]["qy_max"] = _param_get_helper(name="qy_max", category="front_top_panel",
                                                              default_value=0.09234)
        params["front_top_panel"]["match_button"] = _param_get_helper(name="match_button", category="front_top_panel",
                                                                    default_value=False)
        params["front_bottom_panel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
                                                                         category="front_bottom_panel", default_value=0)
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
                                  }
        self.middle_carriage = MiddleCarriage(self, middle_carriage_params)
        front_carriage_params = {"front_carriage": params.get('front_carriage', {}),
                                 "front_dq_values": params.get("front_dq_values", {}),
                                 "front_left_panel": params.get("front_left_panel", {}),
                                 "front_right_panel": params.get("front_right_panel", {}),
                                 "front_top_panel": params.get("front_top_panel", {}),
                                 "front_bottom_panel": params.get("front_bottom_panel", {})
                                 }
        self.front_carriage = FrontCarriage(self, front_carriage_params)

    def calculate_objects(self):
        self.beam.calculate_beam()
        self.collimation.calculate_collimation()
        self.all_carriage.calculate_all_Carriage()
        self.middle_carriage.calculate_middleCarriage()
        self.front_carriage.calculate_frontCarriage()

    # Get methods After here
    def get_wavelength(self):
        return self.beam.wavelength

    def get_l_1(self):
        return self.collimation.l_1

    def get_l_2(self):
        return self.all_carriage.l_2

    def get_source_aperture(self):
        return self.collimation.source_aperture

    def get_sample_aperture(self):
        return self.collimation.sample_aperture

    # Get methods before here

    def sas_calc(self) -> Dict[str, Union[Number, str, List[Union[Number, str]]]]:
        self.calculate_objects()
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
        user_inaccessible["middle_carriage"]["l_2"] = self.all_carriage.l_2
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
        user_inaccessible["front_carriage"]["q_min"] = self.front_carriage.dq_calc.q_min
        user_inaccessible["front_carriage"]["dqx_min"] = self.front_carriage.dq_calc.dqx_min
        user_inaccessible["front_carriage"]["dqy_min"] = self.front_carriage.dq_calc.dqy_min
        user_inaccessible["front_carriage"]["q_max"] = self.front_carriage.dq_calc.q_max
        user_inaccessible["front_carriage"]["dqx_max"] = self.front_carriage.dq_calc.dqx_max
        user_inaccessible["front_carriage"]["dqy_max"] = self.front_carriage.dq_calc.dqy_max
        user_inaccessible["front_carriage"]["ssd_input"] = self.front_carriage.ssd_input
        user_inaccessible["front_carriage"]["ssd"] = self.front_carriage.ssd
        user_inaccessible["front_carriage"]["refBeamCtrX"] = self.front_carriage.refBeamCtr_x
        user_inaccessible["front_carriage"]["RefBeamCtrY"] = self.front_carriage.refBeamCtr_y
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
        constants = VSANS_Constants()
        results = constants.get_constants(preset, _create_vsans_dict(name=False), True)
        results = VSANS.update_source_aperture_with_data(results)
        return check_params(params=results)

    @staticmethod
    def update_source_aperture_with_data(results):
        # Update the number of guides to be correct
        source_aperture_js = results["collimation"]["source_aperture_js"]
        guide_select = results["collimation"]["guide_select"]
        return VSANS.update_source_aperture(results=results, source_aperture_js=source_aperture_js,
                                            guide_select=guide_select)

    @staticmethod
    def update_source_aperture(results=None, source_aperture_js='0.0', guide_select='0'):
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
        # Front Carriage
        params["front_carriage"]["q_min"] = create_number_output(name="Qmin", unit="1/Å", default=0.01875)
        params["front_carriage"]["dqx_min"] = create_number_output(name="(ΔQ/Q_min)_x", unit="1/Å", default=0.05496)
        params["front_carriage"]["dqy_min"] = create_number_output(name="(ΔQ/_Qmin)_y", unit="1/Å", default=0.05503)
        params["front_carriage"]["q_max"] = create_number_output(name="Q_max", unit="1/Å", default=0.1826)
        params["front_carriage"]["dqx_max"] = create_number_output(name="(ΔQ/Q_max)_x", unit="1/Å", default=0.04906)
        params["front_carriage"]["dqy_max"] = create_number_output(name="(ΔQ/_Qmax)_y", unit="1/Å", default=0.04906)
        params["front_carriage"]["ssd_input"] = create_number_input(name="SSD Input", unit="cm", default=400)
        params["front_carriage"]["ssd"] = create_ssd(default=411, readonly=True)
        params["front_carriage"]["refBeamCtrX"] = create_number_input(name="Ref Beam Ctr X", unit="cm", default=0)
        params["front_carriage"]["RefBeamCtrY"] = create_number_input(name="Ref Beam Ctr Y", unit="cm", default=0)
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
