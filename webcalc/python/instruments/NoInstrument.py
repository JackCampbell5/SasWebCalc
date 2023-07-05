import numpy as np
from typing import Dict, Union
import math
from ..instrumentJSParams import create_number_input, create_js


class NoInstrument:
    """A class for storing and manipulating The No Instrument related data.

    :param str self.name: The name of the instrument
    :param int self.n_pts: The number of points to calculate (n_pts for 1D and n_pts^2 for 2D)
    :param float self.arm_to_point: The value of how many points are in an angstrom
    :param str self.spacing: How the spacing of the points should be (Linear or Logarithmic)
    :param float self.q_min: The minimum Q value
    :param float self.dq: The Q resolution of the instrument
    :param float self.q_max: The maximum Q value
    :param float self._q_max_horizon: The maximum horizontal Q value
    :param float self._q_max_vert: THe maximum vertical Q value
    :param float self._q_min_horizon: The minimum horizontal Q value
    :param float self._q_min_vert: The minimum vertical Q value
    :param dict self._params: The dictionary of params passed from the calculate function in web calc
    """
    class_name = "NoInstrument"
    name_shown = "User-Defined Q-Range and Resolutions"

    # Constructor for the pseudo instrument with user-defined Q ranges and instrument resolutions
    def __init__(self, name, params):
        """The constructor method that creates the necessary parameters and runs the load_params method classes constructor
         Sets object parameters self.name, self.n_pts, self.arm_to_point, self.spacing, self.q_min, self.dq, self.q_max, self._q_max_horizon,
         self._q_max_vert, self._q_min_horizon, self._q_min_vert, and self._params

        :param str name: The name of the instrument(Typically set to Q_Range)
        :param dict params: A dictionary of the params
        """
        self.name = name if name else "Q Range"
        self.n_pts = 0
        self.arm_to_point = 25 / 0.3
        self.spacing = 'lin'
        self.q_min = 0.0
        self.dq = 0.0
        self.q_max = 0.0
        self._q_max_horizon = 6.0
        self._q_max_vert = 6.0
        self._q_min_horizon = -6.0
        self._q_min_vert = -6.0
        self._params = params

        self.load_params(params)

    @property
    def q_max_vert(self):
        return self._q_max_vert

    @q_max_vert.setter
    def q_max_vert(self, val: float):
        self._q_max_vert = val
        self.set_q_max()

    @property
    def q_min_vert(self):
        return self._q_min_vert

    @q_min_vert.setter
    def q_min_vert(self, val: float):
        self._q_min_vert = val
        self.set_q_max()

    @property
    def q_max_horizon(self):
        return self._q_max_horizon

    @q_max_horizon.setter
    def q_max_horizon(self, val: float):
        self._q_max_horizon = val
        self.set_q_max()

    @property
    def q_min_horizon(self):
        return self._q_min_horizon

    @q_min_horizon.setter
    def q_min_horizon(self, val: float):
        self._q_min_horizon = val
        self.set_q_max()

    def set_q_max(self):
        """Creates an array of corners and sets the Q_max value to the one with the biggest calculates value

        :return: No return just sets the q_max value
        :rtype: None
        """
        corners = [
            math.sqrt(self.q_max_vert ** 2 + self.q_max_horizon ** 2),
            math.sqrt(self.q_min_vert ** 2 + self.q_max_horizon ** 2),
            math.sqrt(self.q_max_vert ** 2 + self.q_min_horizon ** 2),
            math.sqrt(self.q_min_vert ** 2 + self.q_min_horizon ** 2),
        ]
        self.q_max = max(corners)

    def load_params(self, params: Dict[str, Dict[str, Union[float, int, str]]]):
        """Loads the parameters from the parameters dictionary into the object values

        :param dict params: A dictionary of parameters
        :return: Nothing as it just sets values
        :rtype: None
        """
        print("No Instrument Load Params")
        values = {}
        # Simplify the parameters passed into a key:value pairing instead of a key: {sub_key: value} pairing
        params = params.get('instrument_params', None).get('Settings',None)
        params.pop("name")
        for name, value in params.items():
            def_value = 0.0 if value.get("type", "number") == "number" else "lin"
            values[name] = value.get("default", def_value)
        self.n_pts = values.get('points', 0.0)
        self.spacing = values.get('point_spacing', self.spacing)
        self.q_min = values.get('q_min', self.q_min)
        self.dq = values.get('dq', self.dq)
        self.q_max_vert = values.get('q_max_vertical', self.q_max_vert)
        self.q_min_vert = values.get('q_min_vertical', self.q_min_vert)
        self.q_max_horizon = values.get('q_max_horizontal', self.q_max_horizon)
        self.q_min_horizon = values.get('q_min_horizontal', self.q_min_horizon)

    def sas_calc(self):
        """Calculates the necessary values and arrays to return to the JS
        Calls create_f_sub_s and create_intensity2d and sends the return value to python_return

        :return: A dictionary of encoded parameters from python return
        :rtype: Dict
        """
        q_vals = (np.linspace(self.q_min, self.q_max, self.n_pts) if self.spacing == 'lin' else
                  np.logspace(math.log(self.q_min, 10), math.log(self.q_max, 10), self.n_pts))
        qx_values = np.linspace(self.q_min_horizon, self.q_max_horizon, self.n_pts)
        qy_values = np.linspace(self.q_min_vert, self.q_max_vert, self.n_pts)
        q_2d_vals = np.sqrt(qx_values * qx_values + qy_values * qy_values)
        np.broadcast_to(qx_values, (self.n_pts, len(qx_values)))
        np.broadcast_to(qy_values, (self.n_pts, len(qy_values)))
        dq_vals = q_vals * self.dq
        dqx_vals = qx_values * self.dq
        dqy_vals = qy_values * self.dq
        f_sub_s = self.create_f_sub_s(q_values=q_vals)
        intensity2d = self.create_intensity2d()
        self.one_dimensional = {"I": None, "dI": None, "Q": q_vals, "dQ": dq_vals, "fSubS": f_sub_s}
        self.two_dimensional = {"I": q_2d_vals, "dI": None, "Qx": qx_values, "dQx": dqx_vals, "Qy": qy_values,
                                "dQy": dqy_vals, "intensity2D": intensity2d}
        return self.python_return()

    def create_f_sub_s(self, q_values):
        """Creates the f_sub_s array by looking at if there are any points with a q values less than the q_min value

        :param array q_values: An array of the q values
        :return: An array of the f_sub_s values
        :rtype: Array
        """
        # Take out anything below the Q minimum
        f_sub_s = np.ones(self.n_pts)  # The f_sub_s array
        for num in range(len(q_values)):
            if q_values[num] < self.q_min:
                f_sub_s[num] = 0
        return f_sub_s

    def create_intensity2d(self):
        """Creates a 2D array of intensity values based on q_min and the number of points

        :return: A 2-dimensional array containing the intensity2d values
        :rtype: 2D Array
        """
        stop_points = round(self.arm_to_point * self.q_min)  # How many points to take out of the center
        what_points = []  # An array of The points that should be removed
        odd_points = False  # Is the number of points odd or even?
        center = self.n_pts / 2  # The center of the data

        # If the # of points is less than the size of the beamstop then make all the points 0's
        if self.n_pts <= stop_points or  self.n_pts<3:
            return np.zeros((self.n_pts, self.n_pts))
        else:
            intensity2d = np.ones((self.n_pts, self.n_pts))

        # If the number of points is odd make odd_points true and change the center
        if self.n_pts % 2 == 1:
            odd_points = True
            center = center - .5  # The center of the array
        center = int(center)

        # If the beam stop in points is not length points to be center on the correct number of pixels add a point
        if (odd_points and stop_points % 2 == 0) or (stop_points % 2 == 1 and not odd_points):
            stop_points = stop_points + 1

        # Loops adds the 0's at the correct size points
        if stop_points % 2 == 0:
            for num in range(int(stop_points / 2) + 1):
                what_points.append(center + num)
                what_points.append(center - num - 1)
        else:
            what_points.append(center)
            if stop_points > 1:
                for num in range(int(stop_points / 2 - 0.5)):
                    what_points.append(center + num + 1)
                    what_points.append(center - num - 1)
        what_points.sort()  # Sort the points in order

        # If the points are uneven set the middle to be correctly
        if len(what_points) % 2 == 1:
            # Remove the ones in center
            center_array = what_points[int(len(what_points) / 2 - .5)]
            for num in what_points:
                intensity2d[center_array][num] = 0

        half_len = math.ceil(len(what_points) / 2)
        # Remove in both center
        for num in range(half_len):
            # Creates an array of the points that should be at this cross-section
            if odd_points:
                short_what_points = what_points[half_len - num - 1:half_len + num]
            else:
                short_what_points = what_points[half_len - num - 1:half_len + num + 1]
            # Edit the Array for one side
            for num2 in short_what_points:
                intensity2d[what_points[0 + num]][num2] = 0
            # Edit the array for the other side
            for num2 in short_what_points:
                intensity2d[what_points[len(what_points) - 1 - num]][num2] = 0

        return intensity2d

    def python_return(self):
        """Function that takes all the values calculated and puts them in a python return dictionary

        :return: A dictionary of the python return
        :rtype: Dict
        """
        python_return = {}
        # TODO return the rest  of the calculated values when required by the js
        python_return["fSubs"] = self.one_dimensional.get("fSubS", {}).tolist()
        python_return["qxValues"] = self.two_dimensional.get("Qx", {}).tolist()
        python_return["qyValues"] = self.two_dimensional.get("Qy", {}).tolist()
        python_return["intensity2D"] = self.two_dimensional.get("intensity2D", {})
        python_return["qValues"] = self.one_dimensional.get("Q", {}).tolist()
        return python_return

    @staticmethod
    def get_js_params():
        """Creates a dictionary of js element_parameters to create html elements for NoInstrument

        params["Settings"][elementName] = {element_parameters}

        + **User editable elements:** q_min_vertical, q_max_vertical, q_min_horizontal, q_max_horizontal, q_min, dq,
          points, and point_spacing

        + **element_parameters**: name, default, type_val, unit, readonly, options, step, range_id,hidden, lower_limit,
          and upper_limit


        :return: Completed dictionary params["Settings"][paramName] = js_element_array
        :rtype: Dict
        """
        params = {"Settings": {"name": " "}}
        params["Settings"]["q_min_vertical"] = create_number_input(name='Q Min Vertical', default=-0.3,
                                                                   lower_limit=-2.0, upper_limit=2.0, step=0.1)
        params["Settings"]["q_max_vertical"] = create_number_input(name="Q Max Vertical", default=0.3, lower_limit=-2.0,
                                                                   upper_limit=2.0, step=0.1)
        params["Settings"]["q_min_horizontal"] = create_number_input(name="Q Min Horizontal", default=-0.3,
                                                                     lower_limit=-2.0, upper_limit=2.0, step=0.1)
        params["Settings"]["q_max_horizontal"] = create_number_input(name="Q Max Horizontal", default=0.3,
                                                                     lower_limit=-2.0,
                                                                     upper_limit=2.0, step=0.1)
        params["Settings"]["q_min"] = create_number_input(name="Q Minimum", default=0.01, lower_limit=-2.0,
                                                          upper_limit=2.0, step=0.01)
        params["Settings"]["dq"] = create_number_input(name="Q Resolution", default=10.0, lower_limit=0.0,
                                                       upper_limit="inf", unit="%")
        params["Settings"]["points"] = create_number_input(name="Number of 1D points", default=50, lower_limit=3.0,
                                                           upper_limit=1000)
        params["Settings"]["point_spacing"] = create_js(name="Point Spacing", default="lin", type_val="select",
                                                        options=['lin', 'log'])
        return params
