from ..instrument import Instrument
from ..instrumentJSParams import *


class VSANS(Instrument):
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
        params = self.param_restructure(params)
        # Super is the Instrument class
        super().__init__(name, params)

    def load_params(self, params):
        """A method that loads the constants of the VSANS Instrument

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("VSANS Load Params")

        # Temporary constants not in use any more
        params["temp"] = {}
        params["temp"]["serverName"] = "VSANS.ncnr.nist.gov"

        super().load_objects(params)

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
        params = {"Beam": {"name": "Beam"}, "Collimation": {"name": "Collimation"},
                  "MiddleCarriage": {"name": "Middle Carriage"}, "MidLeftPanel": {"name": "Middle Carriage Left Panel"},
                  "MidRightPanel": {"name": "Middle Carriage Right Panel"}, "FrontCarriage": {"name": "Front Carriage"},
                  "FrontLeftPanel": {"name": "Front Carriage Left Panel"},
                  "FrontRightPanel": {"name": "Front Carriage Right Panel"},
                  "FrontTopPanel": {"name": "Front Carriage Top Panel"},
                  "FrontBottomPanel": {"name": "Front Carriage Bottom Panel"}
                  }
        params["Beam"]["wavelengthInput"] = create_wavelength_input(lower_limit=None, upper_limit=None)
        params["Beam"]["wavelengthSpread"] = create_wavelength_spread(options=[0.02, 0.12, 0.4], default=0.12)
        params["Beam"]["frontendTrans"] = create_number_output(name="Frontend Trans", default=1.0,
                                                               options=[0.5, 1.0, 0.7], unit=None)
        params["Beam"]["flux"] = create_number_output(name="Flux", unit="Φ", default=1.362e+11)
        params["Beam"]["BeamCurrent"] = create_number_output(name="Beam Current", unit="1/s", default=1.055e+5)
        params["Beam"]["iSub0"] = create_number_output(name="I0", unit="1/s/cm^2", default=8.332e+4)
        params["Collimation"]["numGuides"] = create_guide_config(options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "CONV_BEAMS"])
        params["Collimation"]["sourceAperture"] = create_source_aperture(unit="mm", options=[7.5, 15.0, 30.0],
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
        params["MiddleCarriage"]["2θ_min"] = create_number_output(name="2θ_min", unit="rad", default=0.001329)
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
        params["FrontRightPanel"]["lateralOffset"]= create_number_input(name="Lateral Offset", unit="cm",default=6.766)
        params["FrontRightPanel"]["q_Left"] = create_number_output(name="Q_left",unit="1/Å",default=0.01875)
        params["FrontRightPanel"]["q_Right"]= create_number_output(name="Q_right",unit="1/Å",default=0.1188)
        params["FrontRightPanel"]["matchRightMR"] = create_checkbox(name="Match right edge to of MR", default=False)
        params["FrontTopPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset",unit="cm",default=0)
        params["FrontTopPanel"]["qBottom"] = create_number_output(name="Qbottom",unit="1/Å",default=0.001147)
        params["FrontTopPanel"]["q_Top"]= create_number_output(name="q_top",unit="1/Å",default=0.09234)
        params["FrontTopPanel"]["matchTopMR"] = create_checkbox(name="Match Top Edge to MR", default=False)
        params["FrontBottomPanel"]["verticalOffset"] = create_number_input(name="Vertical Offset",unit="cm",default=0)
        params["FrontBottomPanel"]["q_Top"]= create_number_output(name="Q_Top",unit="1/Å",default=-0.003139)
        params["FrontBottomPanel"]["q_Bottom"]= create_number_output(name="Q_Bottom",unit="1/Å",default=-0.09432)
        params["FrontBottomPanel"]["matchBottomMR"] = create_checkbox(name="Match Bottom Edge of MR",default=False)

        params = check_params(params=params)
        return params
