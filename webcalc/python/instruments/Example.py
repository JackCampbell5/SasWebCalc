from typing import Dict, List, Union

from ..instrumentJSParams import *  # You need this to create JS the easy way
from ..instrument import Instrument, set_params

"""This is an example file to show how to create a pluggable instrument that can be added to webcalc.

+ Many calculation methods can be reused from other classes, such as the averaging methods and models calculations.
    + Instrumental resolution should be calculated in the class here and passed to the other calculations.

+ The set params method can be used to set all the values in an object from the params dictionary.
    + You can get `set_params` using the import `from ..instrument import set_params`
"""

DictType = Dict[str, Union[str, float, int, bool, List[str]]]


class Example(Instrument):
    """ Documentation about this example class

    + Here you should list all the parameters and their uses
    + 2 class-level variables should be defined. The two should be unique
        + `class_name` which is the name of the class so in this example it should be 'Example'
        + `name_shown` which will be the name in the combobox listing all available instruments
    +
    """
    class_name = "Example"
    name_shown = "Example"

    # Constructor for the Example instrument
    def __init__(self, name: str, params: DictType):
        """This the constructor method for an object and is used to define the sub objects and run the set params
        methods

        :param str name: The name of the instrument
        :param dict params: A dictionary of the parameters passed from the calculate instrument method
        :return: Nothing just runs the message
        :rtype: None
        """
        self.name = name if name else "example"
        params = self.param_restructure(params)
        super().__init__(name, params)

    def param_restructure(self, calculate_params: DictType) -> DictType:
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

    def load_params(self, params: DictType):
        """A method that loads the constants to be added to the params dict

        :param dict params: The dictionary of parameters from the __init__ statement
        :return: Nothing, just runs the instrument load objects method
        :rtype: None
        """
        print("Example Load Params")

    def sas_calc(self) -> DictType:
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
        """The base instrumental calculations should be performed here for the resolution."""
        pass

    @staticmethod
    def get_js_params() -> DictType:
        """Creates a dictionary of js element_parameters to create html elements for the example

        `params[category][elementName] = {element_parameters}`
            + This creates an HTML heading called 'category' with an indented input with the id 'elementName'.
            + Values not provided are given default values specified below.
            + The **element_parameters** dictionary takes the form:
                + `name`: The label that accompanies the input. *Required*
                    If no name is provided, no HTML input will be created.
                + `default`: The default value the input should use when first loaded. Default: Empty/None
                + `type_val`: The input type that should be displayed, e.g. 'select' for a combobox, 'range' for
                    a slider, and 'number' for a numerical input. Text boxes are not allowed. Default: numeric
                + `unit`: The expected units of the input. The units will be displayed to the left of the input.
                    Default: None
                + `readonly`: True if the value in the input is for display only and should not be user editable.
                    Default: False
                + `options`: A list of selectable values for a combobox or defaults for a slider element. Default: None
                + `range_id`:
                + `hidden`: Should the element be hidden by default, e.g. an input box should be visible only when a
                    specific option or options are selected from a combobox. Default: False
                + `lower_limit`: The lowest value a numerical input should allow. Default: -infinity
                + `upper_limit`: The largest value a numerical input should allow. Default: infinity

        Helper methods available in instrumentJSParams
            + generate_js_array(): Generates a base set of categories used by most neutron instruments.
            + create_js(): Accepts named parameters and generates a dictionary mapping arg to value.

        :return: Completed dictionary params[category][paramName] = {element_parameters}
        :rtype: Dict
        """
        params = generate_js_array()
        params["Sample"]["sampleTable"] = create_sample_table()

        params["hidden"]["secondary_elements"] = encode_secondary_elements()
        params = check_params(params=params)
        return params
