from ..instrumentJSParams import *  # You need this to create JS the easy way

"""This is an example file to show how to create a class to allow it to correctly be modular


+ In making an instrument it is recommended to do all of the calculations in sub objects and just create the JS and run 
    the calculations from this class

+ The set params method can be used to set all the self values in an object from the params dictionary 
    + You can get set params by running from ..instrument import set_params
"""


class Example:
    """ Documentation about this example class

    + Here you should list all the self params and there uses that are found in the __init__ statement
    + You need 2 things defined at the top of your class not in the __init__ statement
        + First is a class name which is the name of the class so in this example is Example
        + Next is a name shown which will be the name shown in the drop-down of instruments
    +


    :param str self.name: The name of the instrument
    """
    class_name = "NG7SANS"
    name_shown = "NG7 SANS"

    # Constructor for the NG7SANS instrument
    def __init__(self, name, params):
        """This the constructor method for an object and is used to define the sub objects and run the set params
        methods

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = name if name else "example"
        params = self.param_restructure(params)  # Super is the Instrument class

    def param_restructure(self, calculate_params):
        """ This method takes all the parameters provided in the JS format and translates it into something python can understand

        :param dict calculate_params: A dictionary of the values gotten from the js
        :return: An array of the params
        :rtype: Dict
        """
        old_params = calculate_params["instrument_params"]

        def _param_get_helper(name="", category="", key="default", default_value=None, division=1):
            """ Checks if a value exists at a certain key and if not sets the value to none ot be removed later

            :param str name: the dictionary of parameters to get the value from
            :param str key: The name of the key you want the value of
            :param default_value: The default value if none exists at that location in the params dictionary
            :param int division: The number to device by if necessary for debuting
            :return: The value at the keys position in the dictionary or None
            :rtype: str, None
            """
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

        # Instrument class parameters
        self.beam_flux = _param_get_helper(name="beamFlux", category="Wavelength")

        params = {}

        # Below goes all the dictionary's and sub dictionary's in the params array
        self.load_params(params=params)
        return params

    def load_params(self, params):
        """A method that loads the constants to be added to the params dict

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("Example Load Params")

    def sas_calc(self):
        """ The main function that runs all the calculation and returns the results runs
        calculate_instrument_parameters and then writes the return array which each value of user inaccessible
        corresponds to a  js  and the rest of the dictionary's are used for graphing

        Makes a user inaccessible sub dictionary witch contains the results to be sent back to the instrument JS

        :return: A dictionary of the calculation results
        :rtype: Dict
        """
        # MainFunction for this class

        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculate_instrument_parameters()

        # Final output returned to the JS
        python_return = {}
        python_return["user_inaccessible"] = {}
        # TODO Question: Do we even use half of thease
        python_return["qValues"] = self.slicer.q_values.tolist()
        python_return["fSubs"] = self.slicer.f_subs.tolist()
        python_return["qxValues"] = self.slicer.qx_values.tolist()
        python_return["qyValues"] = self.slicer.qy_values.tolist()
        python_return["intensity2D"] = self.slicer.intensity_2D.tolist()
        return python_return

    def calculate_instrument_parameters(self):
        pass

    @staticmethod
    def get_js_params():
        """Creates a dictionary of js element_parameters to create html elements for the example

        params[category][elementName] = {element_parameters}

        + **User editable elements:** -- List here

        + **Read only elements:** -- List here

        + **element_parameters**:  -- list here


        :return: Completed dictionary params[category][paramName] = js_element_array
        :rtype: Dict
        """
        params = generate_js_array()
        params["Sample"]["sampleTable"] = create_sample_table()

        params["hidden"]["secondary_elements"] = encode_secondary_elements()
        params = check_params(params=params)
        return params
