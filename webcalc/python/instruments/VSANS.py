from ..instrument import Instrument
from ..instrumentJSParams import *
from typing import Dict, List, Union
from ..instrumentVSANS import *
from ..constants import VSANS_Constants

Number = Union[float, int]


def _create_vsans_dict(name=True):
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
        self.options = {}
        self.beam = None
        self.collimation = None
        self.middle_Carriage = None
        self.front_Carriage = None
        self.constants = VSANS_Constants().get_constants(self.preset, _create_vsans_dict(name=False))
        # Super is the Instrument class
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

    def param_restructure(self, params):
        old_params = params["instrument_params"]

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

        params = _create_vsans_dict(name=False)
        params["Preset"] = _param_get_helper(name="Presets", category="Presets", default_value="19m")
        params["Beam"]["wavelength"] = _param_get_helper(name="wavelength", category="Beam", default_value=6.0)
        params["Beam"]["dlambda"] = _param_get_helper(name="dlambda", category="Beam", default_value=0.12)
        params["Beam"]["frontendTrans"] = _param_get_helper(name="frontendTrans", category="Beam", default_value=1.0)
        params["Beam"]["flux"] = _param_get_helper(name="flux", category="Beam", default_value=1.362e+11)
        params["Beam"]["beamCurrent"] = _param_get_helper(name="beamCurrent", category="Beam", default_value=1.055e+5)
        params["Beam"]["iSub0"] = _param_get_helper(name="iSub0", category="Beam", default_value=8.332e+4)
        params["Collimation"]["numGuides"] = _param_get_helper(name="numGuides", category="Collimation",
                                                               default_value=0)
        params["Collimation"]["sourceAperture_js"] = _param_get_helper(name="sourceAperture_js", category="Collimation",
                                                                       default_value=30.0)
        params["Collimation"]["sourceDistance"] = _param_get_helper(name="sourceDistance", category="Collimation",
                                                                    default_value=2441)
        params["Collimation"]["t_filter"] = _param_get_helper(name="t_filter", category="Collimation",
                                                              default_value=0.5062523594147008)
        params["Collimation"]["t_guide"] = _param_get_helper(name="t_guide", category="Collimation", default_value=1)
        params["Collimation"]["extSampleAperture"] = _param_get_helper(name="extSampleAperture", category="Collimation",
                                                                       default_value=12.7)
        params["Collimation"]["sampleToApGv"] = _param_get_helper(name="sampleToApGv", category="Collimation",
                                                                  default_value=22)
        params["Collimation"]["sampleToGv"] = _param_get_helper(name="sampleToGv", category="Collimation",
                                                                default_value=22)
        params["Collimation"]["l_1"] = _param_get_helper(name="l_1", category="Collimation", default_value=2419)
        params["Collimation"]["aOverL"] = _param_get_helper(name="aOverL", category="Collimation",
                                                            default_value=0.000001530)
        params["MiddleCarriage"]["ssdInput"] = _param_get_helper(name="ssdInput", category="MiddleCarriage",
                                                                 default_value=1900)
        params["MiddleCarriage"]["ssd"] = _param_get_helper(name="ssd", category="MiddleCarriage", default_value=1911)
        params["MiddleCarriage"]["L_2"] = _param_get_helper(name="L_2", category="MiddleCarriage", default_value=1922)
        params["MiddleCarriage"]["beamDrop"] = _param_get_helper(name="beamDrop", category="MiddleCarriage",
                                                                 default_value=0.9414)
        params["MiddleCarriage"]["beamstopRequired"] = _param_get_helper(name="beamstopRequired",
                                                                         category="MiddleCarriage", default_value=2.014)
        params["MiddleCarriage"]["Beamstop"] = _param_get_helper(name="Beamstop", category="MiddleCarriage",
                                                                 default_value=2)
        params["MiddleCarriage"]["θ2_min"] = _param_get_helper(name="θ2_min", category="MiddleCarriage",
                                                               default_value=0.001329)
        params["MiddleCarriage"]["q_min"] = _param_get_helper(name="q_min", category="MiddleCarriage",
                                                              default_value=0.001392)
        params["MiddleCarriage"]["dQx_Middle_min"] = _param_get_helper(name="dQx_Middle_min", category="MiddleCarriage",
                                                                       default_value=0.3393)
        params["MiddleCarriage"]["dQy_Middle_min"] = _param_get_helper(name="dQy_Middle_min", category="MiddleCarriage",
                                                                       default_value=0.3412)
        params["MiddleCarriage"]["qMax"] = _param_get_helper(name="qMax", category="MiddleCarriage",
                                                             default_value=0.03818)
        params["MiddleCarriage"]["dQx_Middle_max"] = _param_get_helper(name="dQx_Middle_max", category="MiddleCarriage",
                                                                       default_value=0.05050)
        params["MiddleCarriage"]["dQy_Middle_max"] = _param_get_helper(name="dQy_Middle_max", category="MiddleCarriage",
                                                                       default_value=0.05051)
        params["MiddleCarriage"]["refBeamCtr_x"] = _param_get_helper(name="refBeamCtr_x", category="MiddleCarriage",
                                                                     default_value=0)
        params["MiddleCarriage"]["refBeamCtr_y"] = _param_get_helper(name="refBeamCtr_y", category="MiddleCarriage",
                                                                     default_value=0)
        params["MidLeftPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="MidLeftPanel",
                                                                    default_value=-6)
        params["MidLeftPanel"]["Q_right"] = _param_get_helper(name="Q_right", category="MidLeftPanel",
                                                              default_value=0.003822)
        params["MidLeftPanel"]["qx_ML_min"] = _param_get_helper(name="qx_ML_min", category="MidLeftPanel",
                                                                default_value=-0.02545)
        params["MidRightPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="MidRightPanel",
                                                                     default_value=-5.5)
        params["MidRightPanel"]["qx_MR_min"] = _param_get_helper(name="qx_MR_min", category="MidRightPanel",
                                                                 default_value=-0.002622)
        params["MidRightPanel"]["qx_MR_max"] = _param_get_helper(name="qx_MR_max", category="MidRightPanel",
                                                                 default_value=0.01901)
        params["MidRightPanel"]["qy_MR_min"] = _param_get_helper(name="qy_MR_min", category="MidRightPanel",
                                                                 default_value=0.02854)
        params["MidRightPanel"]["qy_MR_max"] = _param_get_helper(name="qy_MR_max", category="MidRightPanel",
                                                                 default_value=0.02809)
        params["FrontCarriage"]["qmin"] = _param_get_helper(name="qmin", category="FrontCarriage",
                                                            default_value=0.01875)
        params["FrontCarriage"]["dQx_Front_min"] = _param_get_helper(name="dQx_Front_min", category="FrontCarriage",
                                                                     default_value=0.05496)
        params["FrontCarriage"]["dQy_Front_min"] = _param_get_helper(name="dQy_Front_min", category="FrontCarriage",
                                                                     default_value=0.05503)
        params["FrontCarriage"]["qMax"] = _param_get_helper(name="qMax", category="FrontCarriage", default_value=0.1826)
        params["FrontCarriage"]["dQx_Front_max"] = _param_get_helper(name="dQx_Front_max", category="FrontCarriage",
                                                                     default_value=0.04906)
        params["FrontCarriage"]["dQy_Front_max"] = _param_get_helper(name="dQy_Front_max", category="FrontCarriage",
                                                                     default_value=0.04906)
        params["FrontCarriage"]["ssd_input"] = _param_get_helper(name="ssd_input", category="FrontCarriage",
                                                                 default_value=400)
        params["FrontCarriage"]["ssd"] = _param_get_helper(name="ssd", category="FrontCarriage", default_value=411)
        params["FrontCarriage"]["refBeamCtrX"] = _param_get_helper(name="refBeamCtrX", category="FrontCarriage",
                                                                   default_value=0)
        params["FrontCarriage"]["RefBeamCtrY"] = _param_get_helper(name="RefBeamCtrY", category="FrontCarriage",
                                                                   default_value=0)
        params["FrontLeftPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="FrontLeftPanel",
                                                                      default_value=-9.24)
        params["FrontLeftPanel"]["q_right"] = _param_get_helper(name="q_right", category="FrontLeftPanel",
                                                                default_value=-0.02538)
        params["FrontLeftPanel"]["q_left"] = _param_get_helper(name="q_left", category="FrontLeftPanel",
                                                               default_value=-0.1253)
        params["FrontLeftPanel"]["matchMLButton"] = _param_get_helper(name="matchMLButton", category="FrontLeftPanel",
                                                                      default_value=False)
        params["FrontRightPanel"]["lateralOffset"] = _param_get_helper(name="lateralOffset", category="FrontRightPanel",
                                                                       default_value=6.766)
        params["FrontRightPanel"]["q_Left"] = _param_get_helper(name="q_Left", category="FrontRightPanel",
                                                                default_value=0.01875)
        params["FrontRightPanel"]["q_Right"] = _param_get_helper(name="q_Right", category="FrontRightPanel",
                                                                 default_value=0.1188)
        params["FrontRightPanel"]["matchRightMR"] = _param_get_helper(name="matchRightMR", category="FrontRightPanel",
                                                                      default_value=False)
        params["FrontTopPanel"]["verticalOffset"] = _param_get_helper(name="verticalOffset", category="FrontTopPanel",
                                                                      default_value=0)
        params["FrontTopPanel"]["qBottom"] = _param_get_helper(name="qBottom", category="FrontTopPanel",
                                                               default_value=0.001147)
        params["FrontTopPanel"]["q_Top"] = _param_get_helper(name="q_Top", category="FrontTopPanel",
                                                             default_value=0.09234)
        params["FrontTopPanel"]["matchTopMR"] = _param_get_helper(name="matchTopMR", category="FrontTopPanel",
                                                                  default_value=False)
        params["FrontBottomPanel"]["verticalOffset"] = _param_get_helper(name="verticalOffset",
                                                                         category="FrontBottomPanel", default_value=0)
        params["FrontBottomPanel"]["q_Top"] = _param_get_helper(name="q_Top", category="FrontBottomPanel",
                                                                default_value=-0.003139)
        params["FrontBottomPanel"]["q_Bottom"] = _param_get_helper(name="q_Bottom", category="FrontBottomPanel",
                                                                   default_value=-0.09432)
        params["FrontBottomPanel"]["matchBottomMR"] = _param_get_helper(name="matchBottomMR",
                                                                        category="FrontBottomPanel",
                                                                        default_value=False)
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
        middle_carriage_params = {"MiddleCarriage": params.get('MiddleCarriage', {}),
                                  "MidLeftPanel": params.get("MidLeftPanel", {}),
                                  "MidRightPanel": params.get("MidRightPanel", {})
                                  }
        self.middle_Carriage = MiddleCarriage(self, middle_carriage_params)
        front_carriage_params = {"FrontCarriage": params.get('FrontCarriage', {}),
                                 "FrontLeftPanel": params.get("FrontLeftPanel", {}),
                                 "FrontRightPanel": params.get("FrontRightPanel", {}),
                                 "FrontTopPanel": params.get("FrontTopPanel", {}),
                                 "FrontBottomPanel": params.get("FrontBottomPanel", {})
                                 }
        self.front_Carriage = FrontCarriage(self, front_carriage_params)

    def calculate_objects(self):
        self.beam.calculate_beam()
        self.collimation.calculate_collimation()
        self.middle_Carriage.calculate_middleCarriage()
        self.front_Carriage.calculate_frontCarriage()

    def sas_calc(self) -> Dict[str, Union[Number, str, List[Union[Number, str]]]]:
        self.calculate_objects()
        user_inaccessible = _create_vsans_dict(name=False)
        user_inaccessible["Beam"]["wavelength"] = self.beam.wavelength
        user_inaccessible["Beam"]["dlambda"] = self.beam.dlambda
        user_inaccessible["Beam"]["frontendTrans"] = self.beam.frontend_trans
        user_inaccessible["Beam"]["flux"] = self.beam.flux
        user_inaccessible["Beam"]["beamCurrent"] = self.beam.beamCurrent
        user_inaccessible["Beam"]["iSub0"] = self.beam.iSub0
        user_inaccessible["Collimation"]["numGuides"] = self.collimation.numGuides
        user_inaccessible["Collimation"]["sourceAperture_js"] = self.collimation.sourceAperture_js
        user_inaccessible["Collimation"]["sourceDistance"] = self.collimation.sourceDistance
        user_inaccessible["Collimation"]["t_filter"] = self.collimation.t_filter
        user_inaccessible["Collimation"]["t_guide"] = self.collimation.t_guide
        user_inaccessible["Collimation"]["extSampleAperture"] = self.collimation.extSampleAperture
        user_inaccessible["Collimation"]["sampleToApGv"] = self.collimation.sampleToApGv
        user_inaccessible["Collimation"]["sampleToGv"] = self.collimation.sampleToGv
        user_inaccessible["Collimation"]["l_1"] = self.collimation.l_1
        user_inaccessible["Collimation"]["aOverL"] = self.collimation.aOverL
        user_inaccessible["MiddleCarriage"]["ssdInput"] = self.middle_Carriage.ssdInput
        user_inaccessible["MiddleCarriage"]["ssd"] = self.middle_Carriage.ssd
        user_inaccessible["MiddleCarriage"]["L_2"] = self.middle_Carriage.L_2
        user_inaccessible["MiddleCarriage"]["beamDrop"] = self.middle_Carriage.beamDrop
        user_inaccessible["MiddleCarriage"]["beamstopRequired"] = self.middle_Carriage.beamstopRequired
        user_inaccessible["MiddleCarriage"]["Beamstop"] = self.middle_Carriage.Beamstop
        user_inaccessible["MiddleCarriage"]["θ2_min"] = self.middle_Carriage.θ2_min
        user_inaccessible["MiddleCarriage"]["q_min"] = self.middle_Carriage.q_min
        user_inaccessible["MiddleCarriage"]["dQx_Middle_min"] = self.middle_Carriage.dQx_Middle_min
        user_inaccessible["MiddleCarriage"]["dQy_Middle_min"] = self.middle_Carriage.dQy_Middle_min
        user_inaccessible["MiddleCarriage"]["qMax"] = self.middle_Carriage.qMax
        user_inaccessible["MiddleCarriage"]["dQx_Middle_max"] = self.middle_Carriage.dQx_Middle_max
        user_inaccessible["MiddleCarriage"]["dQy_Middle_max"] = self.middle_Carriage.dQy_Middle_max
        user_inaccessible["MiddleCarriage"]["refBeamCtr_x"] = self.middle_Carriage.refBeamCtr_x
        user_inaccessible["MiddleCarriage"]["refBeamCtr_y"] = self.middle_Carriage.refBeamCtr_y
        user_inaccessible["MidLeftPanel"]["lateralOffset"] = self.middle_Carriage.leftPanel.lateralOffset
        user_inaccessible["MidLeftPanel"]["Q_right"] = self.middle_Carriage.leftPanel.Q_right
        user_inaccessible["MidLeftPanel"]["qx_ML_min"] = self.middle_Carriage.leftPanel.qx_ML_min
        user_inaccessible["MidRightPanel"]["lateralOffset"] = self.middle_Carriage.rightPanel.lateralOffset
        user_inaccessible["MidRightPanel"]["qx_MR_min"] = self.middle_Carriage.rightPanel.qx_MR_min
        user_inaccessible["MidRightPanel"]["qx_MR_max"] = self.middle_Carriage.rightPanel.qx_MR_max
        user_inaccessible["MidRightPanel"]["qy_MR_min"] = self.middle_Carriage.rightPanel.qy_MR_min
        user_inaccessible["MidRightPanel"]["qy_MR_max"] = self.middle_Carriage.rightPanel.qy_MR_max
        user_inaccessible["FrontCarriage"]["qmin"] = self.front_Carriage.qmin
        user_inaccessible["FrontCarriage"]["dQx_Front_min"] = self.front_Carriage.dQx_Front_min
        user_inaccessible["FrontCarriage"]["dQy_Front_min"] = self.front_Carriage.dQy_Front_min
        user_inaccessible["FrontCarriage"]["qMax"] = self.front_Carriage.qMax
        user_inaccessible["FrontCarriage"]["dQx_Front_max"] = self.front_Carriage.dQx_Front_max
        user_inaccessible["FrontCarriage"]["dQy_Front_max"] = self.front_Carriage.dQy_Front_max
        user_inaccessible["FrontCarriage"]["ssd_input"] = self.front_Carriage.ssd_input
        user_inaccessible["FrontCarriage"]["ssd"] = self.front_Carriage.ssd
        user_inaccessible["FrontCarriage"]["refBeamCtrX"] = self.front_Carriage.refBeamCtrX
        user_inaccessible["FrontCarriage"]["RefBeamCtrY"] = self.front_Carriage.RefBeamCtrY
        user_inaccessible["FrontLeftPanel"]["lateralOffset"] = self.front_Carriage.leftPanel.lateralOffset
        user_inaccessible["FrontLeftPanel"]["q_right"] = self.front_Carriage.leftPanel.q_right
        user_inaccessible["FrontLeftPanel"]["q_left"] = self.front_Carriage.leftPanel.q_left
        user_inaccessible["FrontLeftPanel"]["matchMLButton"] = self.front_Carriage.leftPanel.matchMLButton
        user_inaccessible["FrontRightPanel"]["lateralOffset"] = self.front_Carriage.rightPanel.lateralOffset
        user_inaccessible["FrontRightPanel"]["q_Left"] = self.front_Carriage.rightPanel.q_Left
        user_inaccessible["FrontRightPanel"]["q_Right"] = self.front_Carriage.rightPanel.q_Right
        user_inaccessible["FrontRightPanel"]["matchRightMR"] = self.front_Carriage.rightPanel.matchRightMR
        user_inaccessible["FrontTopPanel"]["verticalOffset"] = self.front_Carriage.topPanel.verticalOffset
        user_inaccessible["FrontTopPanel"]["qBottom"] = self.front_Carriage.topPanel.qBottom
        user_inaccessible["FrontTopPanel"]["q_Top"] = self.front_Carriage.topPanel.q_Top
        user_inaccessible["FrontTopPanel"]["matchTopMR"] = self.front_Carriage.topPanel.matchTopMR
        user_inaccessible["FrontBottomPanel"]["verticalOffset"] = self.front_Carriage.bottomPanel.verticalOffset
        user_inaccessible["FrontBottomPanel"]["q_Top"] = self.front_Carriage.bottomPanel.q_Top
        user_inaccessible["FrontBottomPanel"]["q_Bottom"] = self.front_Carriage.bottomPanel.q_Bottom
        user_inaccessible["FrontBottomPanel"]["matchBottomMR"] = self.front_Carriage.bottomPanel.matchBottomMR
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
            sourceAperture_js = rest_info[:rest_info.find('+')]
            numGuides = rest_info[rest_info.find('+')+1:]
            return VSANS.update_source_aperture(rest_info,sourceAperture_js=sourceAperture_js,numGuides=numGuides)

    @staticmethod
    def preset_change(preset):
        constants = VSANS_Constants()
        results = constants.get_constants(preset, _create_vsans_dict(name=False), True)
        results = VSANS.update_source_aperture_with_data(results)
        return check_params(params=results)

    @staticmethod
    def update_source_aperture_with_data(results):
        # Update the number of guides to be correct
        sourceAperture_js = results["Collimation"]["sourceAperture_js"]
        numGuides = results["Collimation"]["numGuides"]
        return VSANS.update_source_aperture(results=results, sourceAperture_js=sourceAperture_js, numGuides=numGuides)

    @staticmethod
    def update_source_aperture(results=None, sourceAperture_js=0.0, numGuides=0):
        if results is None: results = {"Collimation": {}, "options": {}}
        if numGuides == 0:
            valid_ops = ['7.5', '15.0', '30.0']
            if not sourceAperture_js in valid_ops:
                sourceAperture_js = '30.0'
        elif numGuides == 'CONV_BEAMS':
            if sourceAperture_js != '6.0':
                sourceAperture_js = '6.0'
            valid_ops = ['6.0']
        else:
            if sourceAperture_js != '60.0':
                sourceAperture_js = '60.0'
            valid_ops = ['60.0']
        results["Collimation"]["sourceAperture_js"] = sourceAperture_js
        results["options"]["sourceAperture_js"] = {"category": "Collimation", "options": valid_ops}
        return results

    @staticmethod
    def get_js_params():
        """Creates a dictionary of js element_parameters to create html elements for the NG7SANS

        params[category][elementName] = {element_parameters}

        + **User editable elements:** sampleTable, wavelengthInput, wavelengthSpread, guideConfig, sourceAperture,
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
        params["Beam"]["frontendTrans"] = create_number_output(name="Frontend Trans", default=1.0,
                                                               options=[0.5, 1.0, 0.7], unit=None)
        params["Beam"]["flux"] = create_number_output(name="Flux", unit="Φ", default=1.362e+11)
        params["Beam"]["beamCurrent"] = create_number_output(name="Beam Current", unit="1/s", default=1.055e+5)
        params["Beam"]["iSub0"] = create_number_output(name="I0", unit="1/s/cm^2", default=8.332e+4)
        params["Collimation"]["numGuides"] = create_guide_config(options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "CONV_BEAMS"]
                                                                 ,extra=0)
        params["Collimation"]["sourceAperture_js"] = create_source_aperture(unit="mm", options=[7.5, 15.0, 30.0],
                                                                            default=30.0)
        params["Collimation"]["sourceDistance"] = create_number_output(name="Source distance", unit="cm", default=2441)
        params["Collimation"]["t_filter"] = create_number_output(name="T_filter", unit=None, default=0.5062523594147008)
        params["Collimation"]["t_guide"] = create_number_output(name="T_guide", unit=None, default=1)
        params["Collimation"]["extSampleAperture"] = create_number_input(name="Ext. Sample aperture", unit="mm",
                                                                         default=12.7, step=0.1)
        params["Collimation"]["sampleToApGv"] = create_number_input(name="Sample ap. to GV", unit="cm", default=22)
        params["Collimation"]["sampleToGv"] = create_number_input(name="Sample to GV", unit="cm", default=11)
        params["Collimation"]["l_1"] = create_number_output(name="L1", unit="cm", default=2419)
        params["Collimation"]["aOverL"] = create_number_output(name="A_1A_2/L_1", unit=None, default=0.000001530)
        # Middle Carriage
        params["MiddleCarriage"]["ssdInput"] = create_number_input(name="SDD input", unit="cm", default=1900)
        params["MiddleCarriage"]["ssd"] = create_number_input(name="SSD", unit="cm", default=1911)
        params["MiddleCarriage"]["L_2"] = create_number_output(name="L_2", unit="cm", default=1922)
        params["MiddleCarriage"]["beamDrop"] = create_number_output(name="Beam Drop", unit="cm", default=0.9414)
        params["MiddleCarriage"]["beamstopRequired"] = create_number_output(name="Beamstop Required", unit="inch",
                                                                            default=2.014)
        params["MiddleCarriage"]["Beamstop"] = create_number_select(name="Beamstop", unit="inch", options=[2, 3, 4],
                                                                    default=2)
        params["MiddleCarriage"]["θ2_min"] = create_number_output(name="2θ_min", unit="rad", default=0.001329)
        params["MiddleCarriage"]["q_min"] = create_number_output(name="Q_min", unit="1/Å", default=0.001392)
        params["MiddleCarriage"]["dQx_Middle_min"] = create_number_output(name="(ΔQ/Qmin)_x", default=0.3393)
        params["MiddleCarriage"]["dQy_Middle_min"] = create_number_output(name="(ΔQ/Q_min)_y", default=0.3412)
        params["MiddleCarriage"]["qMax"] = create_number_output(name="Qmax", unit="1/Å", default=0.03818)
        params["MiddleCarriage"]["dQx_Middle_max"] = create_number_output(name="(ΔQ/Q_max)_x", default=0.05050)
        params["MiddleCarriage"]["dQy_Middle_max"] = create_number_output(name="(ΔQ/Q_max)_y", default=0.05051)
        params["MiddleCarriage"]["refBeamCtr_x"] = create_number_input(name="Ref Beam Ctr_x", default=0, step=0.1,
                                                                       unit="cm")
        params["MiddleCarriage"]["refBeamCtr_y"] = create_number_input(name="Ref Beam Ctr_y", default=0, step=0.1,
                                                                       unit="cm")
        params["MidLeftPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-6)
        params["MidLeftPanel"]["Q_right"] = create_number_output(name="Q_right", unit="1/Å", default=-0.003822)
        params["MidLeftPanel"]["qx_ML_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.02545)
        params["MidRightPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-5.5)
        params["MidRightPanel"]["qx_MR_min"] = create_number_output(name="Q_left", unit="1/Å", default=-0.002622)
        params["MidRightPanel"]["qx_MR_max"] = create_number_output(name="Q_right", unit="1/Å", default=0.01901)
        params["MidRightPanel"]["qy_MR_min"] = create_number_output(name="Q_bottom", unit="1/Å", default=-0.02854)
        params["MidRightPanel"]["qy_MR_max"] = create_number_output(name="Qtop", unit="1/Å", default=0.02809)
        # Front Carriage
        params["FrontCarriage"]["qmin"] = create_number_output(name="Qmin", unit="1/Å", default=0.01875)
        params["FrontCarriage"]["dQx_Front_min"] = create_number_output(name="(ΔQ/Q_min)_x", unit="1/Å",
                                                                        default=0.05496)
        params["FrontCarriage"]["dQy_Front_min"] = create_number_output(name="(ΔQ/_Qmin)_y", unit="1/Å",
                                                                        default=0.05503)
        params["FrontCarriage"]["qMax"] = create_number_output(name="Q_max", unit="1/Å", default=0.1826)
        params["FrontCarriage"]["dQx_Front_max"] = create_number_output(name="(ΔQ/Q_max)_x", unit="1/Å",
                                                                        default=0.04906)
        params["FrontCarriage"]["dQy_Front_max"] = create_number_output(name="(ΔQ/_Qmax)_y", unit="1/Å",
                                                                        default=0.04906)
        params["FrontCarriage"]["ssd_input"] = create_number_input(name="SSD Input", unit="cm", default=400)
        params["FrontCarriage"]["ssd"] = create_ssd(default=411)
        params["FrontCarriage"]["refBeamCtrX"] = create_number_input(name="Ref Beam Ctr X", unit="cm", default=0)
        params["FrontCarriage"]["RefBeamCtrY"] = create_number_input(name="Ref Beam Ctr Y", unit="cm", default=0)
        params["FrontLeftPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm", default=-9.24)
        params["FrontLeftPanel"]["q_right"] = create_number_output(name="Q_right", unit="1/Å", default=-0.02538)
        params["FrontLeftPanel"]["q_left"] = create_number_output(name="Q_left", unit="1/Å", default=-0.1253)
        params["FrontLeftPanel"]["matchMLButton"] = create_checkbox(name="Match to left edge of ML?", default=False)
        params["FrontRightPanel"]["lateralOffset"] = create_number_input(name="Lateral Offset", unit="cm",
                                                                         default=6.766)
        params["FrontRightPanel"]["q_Left"] = create_number_output(name="Q_left", unit="1/Å", default=0.01875)
        params["FrontRightPanel"]["q_Right"] = create_number_output(name="Q_right", unit="1/Å", default=0.1188)
        params["FrontRightPanel"]["matchRightMR"] = create_checkbox(name="Match right edge to of MR", default=False)
        params["FrontTopPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["FrontTopPanel"]["qBottom"] = create_number_output(name="Qbottom", unit="1/Å", default=0.001147)
        params["FrontTopPanel"]["q_Top"] = create_number_output(name="q_top", unit="1/Å", default=0.09234)
        params["FrontTopPanel"]["matchTopMR"] = create_checkbox(name="Match Top Edge to MR", default=False)
        params["FrontBottomPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset", unit="cm", default=0)
        params["FrontBottomPanel"]["q_Top"] = create_number_output(name="Q_Top", unit="1/Å", default=-0.003139)
        params["FrontBottomPanel"]["q_Bottom"] = create_number_output(name="Q_Bottom", unit="1/Å", default=-0.09432)
        params["FrontBottomPanel"]["matchBottomMR"] = create_checkbox(name="Match Bottom Edge of MR", default=False)

        params = check_params(params=params)
        return params
