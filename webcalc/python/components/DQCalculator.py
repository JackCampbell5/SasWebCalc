import math

import numpy as np

from ..instrument import set_params


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

    def __init__(self, parent, params: dict):
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
