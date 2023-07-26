from ..instrument import Instrument
from ..instrumentJSParams import *
from typing import Dict, List, Union
from ..instrumentVSANS import *
from ..constants import VSANS_Constants

Number = Union[float, int]


def _create_vsans_dict(name=True, additional=False):
    vsans_dict = {}
    vsans_dict["Presets"] = {"name": "Presets"} if name else {}
    vsans_dict["Beam"] = {"name": "Beam"} if name else {}
    vsans_dict["Collimation"] = {"name": "Collimation"} if name else {}
    vsans_dict["MiddleCarriage"] = {"name": "Middle Carriage"} if name else {}
    vsans_dict["MidLeftPanel"] = {"name": "Middle Carriage Left Panel"} if name else {}
    vsans_dict["MidRightPanel"] = {"name": "Middle Carriage Right Panel"} if name else {}
    vsans_dict["FrontCarriage"] = {"name": "Front Carriage"} if name else {}
    vsans_dict["FrontLeftPanel"] = {"name": "Front Carriage Left Panel"} if name else {}
    vsans_dict["FrontRightPanel"] = {"name": "Front Carriage Right Panel"} if name else {}
    vsans_dict["FrontTopPanel"] = {"name": "Front Carriage Top Panel"} if name else {}
    vsans_dict["FrontBottomPanel"] = {"name": "Front Carriage Bottom Panel"} if name else {}
    vsans_dict["options"] = {}
    if additional:
        vsans_dict["AllCarriage"] = {}
        vsans_dict["MidDqValues"] = {}
        vsans_dict["FrontDqValues"] = {}
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
        self.preset = params.get('Preset', "19m")
        self.options = {} # {"type": "options", "category": "", "set_to": }
        self.beam = None
        self.all_carriage = None
        self.collimation = None
        self.middle_Carriage = None
        self.front_Carriage = None
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
        params["Beam"]["frontend_trans_options"] = {"0.02": 0.5, "0.12": 1.0, "0.4": 0.7}
        params["Beam"]["lambda_T"] = self.constants.get("lambda_T", 6.2)
        params["Beam"]["phi_0"] = self.constants.get("phi_0", 1.82e13)

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
        params["Preset"] = _param_get_helper(name="Presets", category="Presets", default_value="19m")
        params["Beam"]["wavelength"] = _param_get_helper(name="wavelength", category="Beam", default_value=6.0)
        params["Beam"]["dlambda"] = _param_get_helper(name="dlambda", category="Beam", default_value=0.12)
        params["Beam"]["frontend_trans"] = _param_get_helper(name="frontend_trans", category="Beam", default_value=1.0)
        params["Beam"]["flux"] = _param_get_helper(name="flux", category="Beam", default_value=1.362e+11)
        params["Beam"]["beam_current"] = _param_get_helper(name="beam_current", category="Beam",
                                                            default_value=1.055e+5)
        params["Beam"]["i_sub_zero"] = _param_get_helper(name="i_sub_zero", category="Beam", default_value=8.332e+4)
        params["Collimation"]["guide_select"] = _param_get_helper(name="guide_select", category="Collimation",
                                                                  default_value=0)
        params["Collimation"]["source_aperture_js"] = _param_get_helper(name="source_aperture_js",
                                                                        category="Collimation",
                                                                       default_value=30.0)
        params["Collimation"]["source_distance"] = _param_get_helper(name="source_distance", category="Collimation",
                                                                    default_value=2441)
        params["Collimation"]["t_filter"] = _param_get_helper(name="t_filter", category="Collimation",
                                                              default_value=0.5062523594147008)
        params["Collimation"]["t_guide"] = _param_get_helper(name="t_guide", category="Collimation", default_value=1)
        params["Collimation"]["ext_sample_aperture"] = _param_get_helper(name="ext_sample_aperture",
                                                                        category="Collimation",
                                                                       default_value=12.7)
        params["Collimation"]["sample_to_ap_gv"] = _param_get_helper(name="sample_to_ap_gv", category="Collimation",
                                                                  default_value=22)
        params["Collimation"]["sample_to_gv"] = _param_get_helper(name="sample_to_gv", category="Collimation",
                                                                default_value=22)
        params["Collimation"]["l_1"] = _param_get_helper(name="l_1", category="Collimation", default_value=2419)
        params["Collimation"]["a_over_l"] = _param_get_helper(name="a_over_l", category="Collimation",
                                                            default_value=0.000001530)
        params["MiddleCarriage"]["ssd_input"] = _param_get_helper(name="ssd_input", category="MiddleCarriage",
                                                                 default_value=1900)
        params["MiddleCarriage"]["ssd"] = _param_get_helper(name="ssd", category="MiddleCarriage", default_value=1911)
        params["AllCarriage"]["l_2"] = _param_get_helper(name="l_2", category="MiddleCarriage", default_value=1922)
        params["AllCarriage"]["beam_drop"] = _param_get_helper(name="beam_drop", category="MiddleCarriage",
                                                              default_value=0.9414)
        params["AllCarriage"]["beamstop_required"] = _param_get_helper(name="beamstop_required",
                                                                      category="MiddleCarriage", default_value=2.014)
        params["AllCarriage"]["beamstop"] = _param_get_helper(name="beamstop", category="MiddleCarriage",
                                                              default_value=2)
        params["AllCarriage"]["θ2_min"] = _param_get_helper(name="θ2_min", category="MiddleCarriage",
                                                            default_value=0.001329)
        params["MidDqValues"]["q_min"] = _param_get_helper(name="q_min", category="MiddleCarriage",
                                                           default_value=0.001392)
        params["MidDqValues"]["dqx_min"] = _param_get_helper(name="dqx_min", category="MiddleCarriage",
                                                             default_value=0.3393)
        params["MidDqValues"]["dqx_min"] = _param_get_helper(name="dqx_min", category="MiddleCarriage",
                                                             default_value=0.3412)
        params["MidDqValues"]["q_max"] = _param_get_helper(name="q_max", category="MiddleCarriage",
                                                           default_value=0.03818)
        params["MidDqValues"]["dqx_max"] = _param_get_helper(name="dqx_max", category="MiddleCarriage",
                                                             default_value=0.05050)
        params["MidDqValues"]["dqy_max"] = _param_get_helper(name="dqy_max", category="MiddleCarriage",
                                                             default_value=0.05051)
        params["MiddleCarriage"]["refBeamCtr_x"] = _param_get_helper(name="refBeamCtr_x", category="MiddleCarriage",
                                                                     default_value=0)
        params["MiddleCarriage"]["refBeamCtr_y"] = _param_get_helper(name="refBeamCtr_y", category="MiddleCarriage",
                                                                     default_value=0)
        params["MidLeftPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="MidLeftPanel",
                                                                    default_value=-6)
        params["MidLeftPanel"]["qx_max"] = _param_get_helper(name="qx_max", category="MidLeftPanel",
                                                             default_value=0.003822)
        params["MidLeftPanel"]["qx_min"] = _param_get_helper(name="qx_min", category="MidLeftPanel",
                                                             default_value=-0.02545)
        params["MidRightPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="MidRightPanel",
                                                                     default_value=-5.5)
        params["MidRightPanel"]["qx_min"] = _param_get_helper(name="qx_min", category="MidRightPanel",
                                                              default_value=-0.002622)
        params["MidRightPanel"]["qx_max"] = _param_get_helper(name="qx_max", category="MidRightPanel",
                                                              default_value=0.01901)
        params["MidRightPanel"]["qy_min"] = _param_get_helper(name="qy_min", category="MidRightPanel",
                                                              default_value=0.02854)
        params["MidRightPanel"]["qy_max"] = _param_get_helper(name="qy_max", category="MidRightPanel",
                                                              default_value=0.02809)
        params["FrontDqValues"]["q_min"] = _param_get_helper(name="q_min", category="FrontCarriage",
                                                             default_value=0.01875)
        params["FrontDqValues"]["dqx_min"] = _param_get_helper(name="dqx_min", category="FrontCarriage",
                                                               default_value=0.05496)
        params["FrontDqValues"]["dqy_min"] = _param_get_helper(name="dqy_min", category="FrontCarriage",
                                                               default_value=0.05503)
        params["FrontDqValues"]["q_max"] = _param_get_helper(name="q_max", category="FrontCarriage",
                                                             default_value=0.1826)
        params["FrontDqValues"]["dqx_max"] = _param_get_helper(name="dqx_max", category="FrontCarriage",
                                                               default_value=0.04906)
        params["FrontDqValues"]["dqy_max"] = _param_get_helper(name="dqy_max", category="FrontCarriage",
                                                               default_value=0.04906)
        params["FrontCarriage"]["ssd_input"] = _param_get_helper(name="ssd_input", category="FrontCarriage",
                                                                 default_value=400)
        params["FrontCarriage"]["ssd"] = _param_get_helper(name="ssd", category="FrontCarriage", default_value=411)
        params["FrontCarriage"]["refBeamCtr_x"] = _param_get_helper(name="refBeamCtr_x", category="FrontCarriage",
                                                                    default_value=0)
        params["FrontCarriage"]["refBeamCtr_y"] = _param_get_helper(name="refBeamCtr_y", category="FrontCarriage",
                                                                    default_value=0)
        params["FrontLeftPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="FrontLeftPanel",
                                                                      default_value=-9.24)
        params["FrontLeftPanel"]["qx_max"] = _param_get_helper(name="qx_max", category="FrontLeftPanel",
                                                               default_value=-0.02538)
        params["FrontLeftPanel"]["qx_min"] = _param_get_helper(name="qx_min", category="FrontLeftPanel",
                                                               default_value=-0.1253)
        params["FrontLeftPanel"]["match_button"] = _param_get_helper(name="match_button", category="FrontLeftPanel",
                                                                     default_value=False)
        params["FrontRightPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="FrontRightPanel",
                                                                       default_value=6.766)
        params["FrontRightPanel"]["qx_min"] = _param_get_helper(name="qx_min", category="FrontRightPanel",
                                                                default_value=0.01875)
        params["FrontRightPanel"]["qx_max"] = _param_get_helper(name="qx_max", category="FrontRightPanel",
                                                                default_value=0.1188)
        params["FrontRightPanel"]["match_button"] = _param_get_helper(name="match_button", category="FrontRightPanel",
                                                                      default_value=False)
        params["FrontTopPanel"]["verticalOffset"] = _param_get_helper(name="verticalOffset", category="FrontTopPanel",
                                                                      default_value=0)
        params["FrontTopPanel"]["qy_min"] = _param_get_helper(name="qy_min", category="FrontTopPanel",
                                                              default_value=0.001147)
        params["FrontTopPanel"]["qy_max"] = _param_get_helper(name="qy_max", category="FrontTopPanel",
                                                              default_value=0.09234)
        params["FrontTopPanel"]["match_button"] = _param_get_helper(name="match_button", category="FrontTopPanel",
                                                                    default_value=False)
        params["FrontBottomPanel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
                                                                         category="FrontBottomPanel", default_value=0)
        params["FrontBottomPanel"]["qy_max"] = _param_get_helper(name="qy_max", category="FrontBottomPanel",
                                                                 default_value=-0.003139)
        params["FrontBottomPanel"]["qy_min"] = _param_get_helper(name="qy_min", category="FrontBottomPanel",
                                                                 default_value=-0.09432)
        params["FrontBottomPanel"]["match_button"] = _param_get_helper(name="match_button",
                                                                       category="FrontBottomPanel", default_value=False)
        return params

    def load_objects(self, params):
        """A function that creates the objects necessary for the calculations

        Create objects beam_stops, detectors, collimation, and wavelength

        :param dict params: A dictionary of parameters to send to the initialization of the objects
        :return: Nothing as it just sets up all the objects
        :rtype: None
        """
        self.beam = Beam(self, params.get('Beam', {}))
        self.collimation = Collimation(self, params.get('Collimation', {}))
        self.all_carriage = AllCarriage(self, params.get('AllCarriage', {}))
        middle_carriage_params = {"MiddleCarriage": params.get('MiddleCarriage', {}),
                                  "MidDqValues": params.get("MidDqValues", {}),
                                  "MidLeftPanel": params.get("MidLeftPanel", {}),
                                  "MidRightPanel": params.get("MidRightPanel", {}),
                                  }
        self.middle_Carriage = MiddleCarriage(self, middle_carriage_params)
        front_carriage_params = {"FrontCarriage": params.get('FrontCarriage', {}),
                                 "FrontDqValues": params.get("FrontDqValues", {}),
                                 "FrontLeftPanel": params.get("FrontLeftPanel", {}),
                                 "FrontRightPanel": params.get("FrontRightPanel", {}),
                                 "FrontTopPanel": params.get("FrontTopPanel", {}),
                                 "FrontBottomPanel": params.get("FrontBottomPanel", {})
                                 }
        self.front_Carriage = FrontCarriage(self, front_carriage_params)

    def calculate_objects(self):
        self.beam.calculate_beam()
        self.collimation.calculate_collimation()
        self.all_carriage.calculate_All_Carriage()
        self.middle_Carriage.calculate_middleCarriage()
        self.front_Carriage.calculate_frontCarriage()

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
        user_inaccessible["Beam"]["wavelength"] = self.beam.wavelength
        user_inaccessible["Beam"]["dlambda"] = self.beam.dlambda
        user_inaccessible["Beam"]["frontend_trans"] = self.beam.frontend_trans
        user_inaccessible["Beam"]["flux"] = self.beam.flux
        user_inaccessible["Beam"]["beam_current"] = self.beam.beam_current
        user_inaccessible["Beam"]["i_sub_zero"] = self.beam.i_sub_zero
        user_inaccessible["Collimation"]["guide_select"] = self.collimation.guide_select
        user_inaccessible["Collimation"]["source_aperture_js"] = self.collimation.source_aperture_js
        user_inaccessible["Collimation"]["source_distance"] = self.collimation.source_distance
        user_inaccessible["Collimation"]["t_filter"] = self.collimation.t_filter
        user_inaccessible["Collimation"]["t_guide"] = self.collimation.t_guide
        user_inaccessible["Collimation"]["ext_sample_aperture"] = self.collimation.ext_sample_aperture
        user_inaccessible["Collimation"]["sample_to_ap_gv"] = self.collimation.sample_to_ap_gv
        user_inaccessible["Collimation"]["sample_to_gv"] = self.collimation.sample_to_gv
        user_inaccessible["Collimation"]["l_1"] = self.collimation.l_1
        user_inaccessible["Collimation"]["a_over_l"] = self.collimation.a_over_l
        user_inaccessible["MiddleCarriage"]["ssd_input"] = self.middle_Carriage.ssd_input
        user_inaccessible["MiddleCarriage"]["ssd"] = self.middle_Carriage.ssd
        user_inaccessible["MiddleCarriage"]["l_2"] = self.all_carriage.l_2
        user_inaccessible["MiddleCarriage"]["beam_drop"] = self.all_carriage.beam_drop
        user_inaccessible["MiddleCarriage"]["beamstop_required"] = self.all_carriage.beamstop_required
        user_inaccessible["MiddleCarriage"]["beamstop"] = self.all_carriage.beamstop
        user_inaccessible["MiddleCarriage"]["θ2_min"] = self.all_carriage.θ2_min
        user_inaccessible["MiddleCarriage"]["q_min"] = self.middle_Carriage.dq_calc.q_min
        user_inaccessible["MiddleCarriage"]["dqx_min"] = self.middle_Carriage.dq_calc.dqx_min
        user_inaccessible["MiddleCarriage"]["dqy_min"] = self.middle_Carriage.dq_calc.dqy_min
        user_inaccessible["MiddleCarriage"]["q_max"] = self.middle_Carriage.dq_calc.q_max
        user_inaccessible["MiddleCarriage"]["dqx_max"] = self.middle_Carriage.dq_calc.dqx_max
        user_inaccessible["MiddleCarriage"]["dqy_max"] = self.middle_Carriage.dq_calc.dqy_max
        user_inaccessible["MiddleCarriage"]["refBeamCtr_x"] = self.middle_Carriage.refBeamCtr_x
        user_inaccessible["MiddleCarriage"]["refBeamCtr_y"] = self.middle_Carriage.refBeamCtr_y
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = self.middle_Carriage.left_panel.lateralOffset
        user_inaccessible["MidLeftPanel"]["qx_max"] = self.middle_Carriage.left_panel.qx_max
        user_inaccessible["MidLeftPanel"]["qx_min"] = self.middle_Carriage.left_panel.qx_min
        user_inaccessible["MidRightPanel"]["lateralOffset"] = self.middle_Carriage.right_panel.lateralOffset
        user_inaccessible["MidRightPanel"]["qx_min"] = self.middle_Carriage.right_panel.qx_min
        user_inaccessible["MidRightPanel"]["qx_max"] = self.middle_Carriage.right_panel.qx_max
        user_inaccessible["MidRightPanel"]["qy_min"] = self.middle_Carriage.right_panel.qy_min
        user_inaccessible["MidRightPanel"]["qy_max"] = self.middle_Carriage.right_panel.qy_max
        user_inaccessible["FrontCarriage"]["q_min"] = self.front_Carriage.dq_calc.q_min
        user_inaccessible["FrontCarriage"]["dqx_min"] = self.front_Carriage.dq_calc.dqx_min
        user_inaccessible["FrontCarriage"]["dqy_min"] = self.front_Carriage.dq_calc.dqy_min
        user_inaccessible["FrontCarriage"]["q_max"] = self.front_Carriage.dq_calc.q_max
        user_inaccessible["FrontCarriage"]["dqx_max"] = self.front_Carriage.dq_calc.dqx_max
        user_inaccessible["FrontCarriage"]["dqy_max"] = self.front_Carriage.dq_calc.dqy_max
        user_inaccessible["FrontCarriage"]["ssd_input"] = self.front_Carriage.ssd_input
        user_inaccessible["FrontCarriage"]["ssd"] = self.front_Carriage.ssd
        user_inaccessible["FrontCarriage"]["refBeamCtrX"] = self.front_Carriage.refBeamCtr_x
        user_inaccessible["FrontCarriage"]["RefBeamCtrY"] = self.front_Carriage.refBeamCtr_y
        user_inaccessible["FrontLeftPanel"]["lateralOffset"] = self.front_Carriage.left_panel.lateralOffset
        user_inaccessible["FrontLeftPanel"]["qx_max"] = self.front_Carriage.left_panel.qx_max
        user_inaccessible["FrontLeftPanel"]["qx_min"] = self.front_Carriage.left_panel.qx_min
        user_inaccessible["FrontLeftPanel"]["match_button"] = self.front_Carriage.left_panel.match_button
        user_inaccessible["FrontRightPanel"]["lateralOffset"] = self.front_Carriage.right_panel.lateralOffset
        user_inaccessible["FrontRightPanel"]["qx_min"] = self.front_Carriage.right_panel.qx_min
        user_inaccessible["FrontRightPanel"]["qx_max"] = self.front_Carriage.right_panel.qx_max
        user_inaccessible["FrontRightPanel"]["match_button"] = self.front_Carriage.right_panel.match_button
        user_inaccessible["FrontTopPanel"]["verticalOffset"] = self.front_Carriage.top_panel.verticalOffset
        user_inaccessible["FrontTopPanel"]["qy_min"] = self.front_Carriage.top_panel.qy_min
        user_inaccessible["FrontTopPanel"]["qy_max"] = self.front_Carriage.top_panel.qy_max
        user_inaccessible["FrontTopPanel"]["match_button"] = self.front_Carriage.top_panel.match_button
        user_inaccessible["FrontBottomPanel"]["verticalOffset"] = self.front_Carriage.bottom_panel.verticalOffset
        user_inaccessible["FrontBottomPanel"]["qy_max"] = self.front_Carriage.bottom_panel.qy_max
        user_inaccessible["FrontBottomPanel"]["qy_min"] = self.front_Carriage.bottom_panel.qy_min
        user_inaccessible["FrontBottomPanel"]["match_button"] = self.front_Carriage.bottom_panel.match_button
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
        source_aperture_js = results["Collimation"]["source_aperture_js"]
        guide_select = results["Collimation"]["guide_select"]
        return VSANS.update_source_aperture(results=results, source_aperture_js=source_aperture_js,
                                            guide_select=guide_select)

    @staticmethod
    def update_source_aperture(results=None, source_aperture_js='0.0', guide_select='0'):
        if results is None: results = {"Collimation": {}, "options": {}}
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
        results["Collimation"]["source_aperture_js"] = source_aperture_js
        results["options"]["Collimation+ source_aperture_js"] = {"type": "options", "set_to": valid_ops}
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
        params["Presets"]["Preset"] = create_number_select(name="Presets", options=["19m", "16m", "11m", "4.5m"],
                                                           default="19m", extra="19m")  # The Extra parameter saves
        # the previous value of the preset, so we can check if it has changed
        params["Beam"]["wavelength"] = create_wavelength_input(lower_limit=None, upper_limit=None)
        params["Beam"]["dlambda"] = create_wavelength_spread(options=[0.02, 0.12, 0.4], default=0.12)
        params["Beam"]["frontend_trans"] = create_number_output(name="Frontend Trans", default=1.0,
                                                               options=[0.5, 1.0, 0.7], unit=None)
        params["Beam"]["flux"] = create_number_output(name="Flux", unit="Φ", default=1.362e+11)
        params["Beam"]["beam_current"] = create_number_output(name="Beam Current", unit="1/s", default=1.055e+5)
        params["Beam"]["i_sub_zero"] = create_number_output(name="I0", unit="1/s/cm^2", default=8.332e+4)
        params["Collimation"]["guide_select"] = create_guide_config(options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "CONV_BEAMS"], extra=0)
        params["Collimation"]["source_aperture_js"] = create_source_aperture(unit="mm", options=[7.5, 15.0, 30.0],
                                                                             default=30.0)
        params["Collimation"]["source_distance"] = create_number_output(name="Source distance", unit="cm", default=2441)
        params["Collimation"]["t_filter"] = create_number_output(name="T_filter", unit=None, default=0.5062523594147008)
        params["Collimation"]["t_guide"] = create_number_output(name="T_guide", unit=None, default=1)
        params["Collimation"]["ext_sample_aperture"] = create_number_input(name="Ext. Sample aperture", unit="mm",
                                                                         default=12.7, step=0.1)
        params["Collimation"]["sample_to_ap_gv"] = create_number_input(name="Sample ap. to GV", unit="cm", default=22)
        params["Collimation"]["sample_to_gv"] = create_number_input(name="Sample to GV", unit="cm", default=11)
        params["Collimation"]["l_1"] = create_number_output(name="L1", unit="cm", default=2419)
        params["Collimation"]["a_over_l"] = create_number_output(name="A_1A_2/L_1", unit=None, default=0.000001530)
        # Middle Carriage
        params["MiddleCarriage"]["ssd_input"] = create_number_input(name="SDD input", unit="cm", default=1900)
        params["MiddleCarriage"]["ssd"] = create_number_input(name="SSD", unit="cm", default=1911, readonly=True)
        params["MiddleCarriage"]["l_2"] = create_number_output(name="l_2", unit="cm", default=1922)
        params["MiddleCarriage"]["beam_drop"] = create_number_output(name="Beam Drop", unit="cm", default=0.9414)
        params["MiddleCarriage"]["beamstop_required"] = create_number_output(name="Beamstop Required", unit="inch",
                                                                             default=2.014)
        params["MiddleCarriage"]["beamstop"] = create_number_select(name="beamstop", unit="inch", options=[2, 3, 4],default=2)
        params["MiddleCarriage"]["θ2_min"] = create_number_output(name="2θ_min", unit="rad", default=0.001329)
        params["MiddleCarriage"]["q_min"] = create_number_output(name="Q_min", unit="1/Å", default=0.001392)
        params["MiddleCarriage"]["dqx_min"] = create_number_output(name="(ΔQ/Qmin)_x", default=0.3393)
        params["MiddleCarriage"]["dqy_min"] = create_number_output(name="(ΔQ/Q_min)_y", default=0.3412)
        params["MiddleCarriage"]["q_max"] = create_number_output(name="Qmax", unit="1/Å", default=0.03818)
        params["MiddleCarriage"]["dqx_max"] = create_number_output(name="(ΔQ/Q_max)_x", default=0.05050)
        params["MiddleCarriage"]["dqy_max"] = create_number_output(name="(ΔQ/Q_max)_y", default=0.05051)
        params["MiddleCarriage"]["refBeamCtr_x"] = create_number_input(name="Ref Beam Ctr_x", default=0, step=0.1,unit="cm")
        params["MiddleCarriage"]["refBeamCtr_y"] = create_number_input(name="Ref Beam Ctr_y", default=0, step=0.1,unit="cm")
        params["MidLeftPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-6)
        params["MidLeftPanel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.003822)
        params["MidLeftPanel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.02545)
        params["MidRightPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-5.5)
        params["MidRightPanel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.002622)
        params["MidRightPanel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.01901)
        params["MidRightPanel"]["qy_min"] = create_number_output(name="Q_bottom", unit="1/Å", default=-0.02854)
        params["MidRightPanel"]["qy_max"] = create_number_output(name="Qtop", unit="1/Å", default=0.02809)
        # Front Carriage
        params["FrontCarriage"]["q_min"] = create_number_output(name="Qmin", unit="1/Å", default=0.01875)
        params["FrontCarriage"]["dqx_min"] = create_number_output(name="(ΔQ/Q_min)_x", unit="1/Å",default=0.05496)
        params["FrontCarriage"]["dqy_min"] = create_number_output(name="(ΔQ/_Qmin)_y", unit="1/Å",default=0.05503)
        params["FrontCarriage"]["q_max"] = create_number_output(name="Q_max", unit="1/Å", default=0.1826)
        params["FrontCarriage"]["dqx_max"] = create_number_output(name="(ΔQ/Q_max)_x", unit="1/Å",default=0.04906)
        params["FrontCarriage"]["dqy_max"] = create_number_output(name="(ΔQ/_Qmax)_y", unit="1/Å",default=0.04906)
        params["FrontCarriage"]["ssd_input"] = create_number_input(name="SSD Input", unit="cm", default=400)
        params["FrontCarriage"]["ssd"] = create_ssd(default=411, readonly=True)
        params["FrontCarriage"]["refBeamCtrX"] = create_number_input(name="Ref Beam Ctr X", unit="cm", default=0)
        params["FrontCarriage"]["RefBeamCtrY"] = create_number_input(name="Ref Beam Ctr Y", unit="cm", default=0)
        params["FrontLeftPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-9.24)
        params["FrontLeftPanel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=-0.02538)
        params["FrontLeftPanel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.1253)
        params["FrontLeftPanel"]["match_button"] = create_checkbox(name="Match to left edge of ML?", default=False)
        params["FrontRightPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm",default=6.766)
        params["FrontRightPanel"]["qx_min"] = create_number_output(name="Q_left", unit="1/Å", default=0.01875)
        params["FrontRightPanel"]["qx_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.1188)
        params["FrontRightPanel"]["match_button"] = create_checkbox(name="Match right edge to of MR", default=False)
        params["FrontTopPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["FrontTopPanel"]["qy_min"] = create_number_output(name="Qbottom", unit="1/Å", default=0.001147)
        params["FrontTopPanel"]["qy_max"] = create_number_output(name="q_top", unit="1/Å", default=0.09234)
        params["FrontTopPanel"]["match_button"] = create_checkbox(name="Match Top Edge to MR", default=False)
        params["FrontBottomPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["FrontBottomPanel"]["qy_max"] = create_number_output(name="Q_Top", unit="1/Å", default=-0.003139)
        params["FrontBottomPanel"]["qy_min"] = create_number_output(name="Q_Bottom", unit="1/Å", default=-0.09432)
        params["FrontBottomPanel"]["match_button"] = create_checkbox(name="Match Bottom Edge of MR", default=False)

        params = check_params(params=params)
        return params
