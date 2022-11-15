# TODO: Create slicer class and child slicers
# built-in imports
import math

import numpy as np


#  Calculate the x or y distance from the beam center of a given pixel
def calculate_distance_from_beam_center(pixel_value, pixel_center, pixel_size, coeff):
    if isinstance(pixel_value, np.ndarray):
        pixel_center = np.full(pixel_value.shape, pixel_center)
    return coeff * np.tan((pixel_value - pixel_center) * pixel_size / coeff)


def set_params(instance, params):
    """
    Set class attributes based on a dictionary of values. The dict should map <param_name> -> <value>.
    Args:
        instance: An instance of any class type in this file that needs params set in bulk.
        params: A dict mapping <param_name> -> <value> where param_name should be a known class attribute.
    Returns: None
    """
    if isinstance(params, (list, tuple)):
        # If a list is passed, try using the first value in the list
        params = params[0]
    if not isinstance(params, dict):
        # Retain existing attributes if params are not formatted properly
        print(f"Parameters of type {type(params)} are not allowed when setting params. Please pass a dictionary.")
        return
    for key, value in params.items():
        if hasattr(instance, key):
            # Set known attributes
            setattr(instance, key, value)
        else:
            # Print unrecognized attributes to the console
            print(f"The parameter {key} is not a known {instance} attribute. Unable to set it to {value}.")


class Slicer:

    def __init__(self, params):

        # Import all parameters for slicer class

        # Params needed for calculate_q_range_slicer
        self.mask: np.array = np.zeros_like(0)
        self.intensity_2D: np.array = np.zeros_like(0)
        self.detector_distance: float = 0.0
        self.x_pixels: int = 0
        self.y_pixels: int = 0

        # Values are the default values
        # Q values
        self.qx_values = np.zeros_like(0)
        self.qy_values = np.zeros_like(0)
        # Max and Min Q values
        self.max_qx: float = 0.0
        self.max_qy: float = 0.0
        self.min_qx: float = 0.0
        self.min_qy: float = 0.0

        # Averaging Parameters
        self.detector_sections: str = 'both'
        self.phi: float = 0.0
        self.d_phi: float = math.pi / 2
        self.q_center: float = 0.0
        self.q_width: float = 0.3
        self.aspect_ratio: float = 1.0

        # Instrumental Parameters
        # TODO: Maybe pass the instrument class as a parameter...
        self.lambda_val: float = 6.0
        self.lambda_width: float = 0.14
        self.guides: int = 0
        self.source_aperture: float = 25.4
        self.sample_aperture: float = 6.35
        self.aperture_offset: float = 5.00
        self.beam_stop_size: float = 5.08
        self.SSD: float = 1627
        self.SDD: float = 1530
        # TODO: not all pixels are square => differentiate pixel_size_x from pixel_size_y
        self.pixel_size = 5.08
        self.coeff: float = 10000
        self.x_center: float = 64.5
        self.y_center: float = 64.5

        # Calculate parameters
        self.phi_upper: float = 0.0
        self.phi_lower: float = 0.0
        self.phi_x: float = 0.0
        self.phi_y: float = 0.0
        self.phi_to_ur_corner: float = 0.0
        self.phi_to_ul_corner: float = 0.0
        self.phi_to_ll_corner: float = 0.0
        self.phi_to_lr_corner: float = 0.0

        # set params
        # TODO: set_params should be a class method
        set_params(self, params)
        self.calculate_q_range_slicer()
        self.set_values()

    def set_values(self):
        # Sets the max and min q values and all the phi values

        # Min and max Q value
        self.max_qx = 0.3 if max(self.qx_values) == 0.0 else max(self.qx_values)
        self.max_qy = 0.3 if max(self.qy_values) == 0.0 else max(self.qy_values)
        self.min_qx = 0.0 if min(self.qx_values) == 0.0 else min(self.qx_values)
        self.min_qy = 0.0 if min(self.qy_values) == 0.0 else min(self.qy_values)

        # Calculated parameters
        self.phi_upper = self.phi * self.d_phi
        self.phi_lower = self.phi - self.d_phi
        self.phi_x = math.cos(self.phi)
        self.phi_y = math.sin(self.phi)
        self.phi_to_ur_corner = math.atan(self.max_qy / self.max_qx)
        self.phi_to_ul_corner = math.atan(self.max_qy / self.min_qx) + math.pi
        self.phi_to_ll_corner = math.atan(self.min_qy / self.min_qx) + math.pi
        self.phi_to_lr_corner = math.atan(self.min_qy / self.max_qx) + 2 * math.pi

    # Calculate Q Range Slicer and its helper methods
    def calculate_q_range_slicer(self):
        # Detector values pixel size in mm
        self.intensity_2D = self.generate_ones_data()
        self.mask = self.generate_standard_mask()
        # Calculate Qx and Qy values
        x_pixels = np.array([i for i in range(self.x_pixels)])
        x_distances = calculate_distance_from_beam_center(x_pixels, self.x_center, self.pixel_size, self.coeff)
        theta_x = np.arctan(x_distances / self.detector_distance) / 2
        self.qx_values = (4 * math.pi / self.lambda_val) * np.sin(theta_x)
        y_pixels = np.array([i for i in range(self.y_pixels)])
        y_distances = calculate_distance_from_beam_center(y_pixels, self.y_center, self.pixel_size, self.coeff)
        theta_y = np.arctan(y_distances / self.detector_distance) / 2
        self.qy_values = (4 * math.pi / self.lambda_val) * np.sin(theta_y)

    def generate_ones_data(self) -> np.array:
        return np.ones((self.x_pixels, self.y_pixels))

    # Generate a standard SANS mask with the outer 2 pixels masked
    def generate_standard_mask(self):
        mask = [[1 if i <= 1 or i >= self.x_pixels - 2 or j <= 1 or j >= (self.y_pixels - 2) else 0
                 for i in range(self.x_pixels)] for j in range(self.y_pixels)]
        return np.asarray(mask)


class Circular(Slicer):
    def __init__(self, params):
        super().__init__(params)


class Sector(Slicer):
    def __init__(self, params):
        super().__init__(params)


class Rectangular(Slicer):
    def __init__(self, params):
        super().__init__(params)


class Elliptical(Slicer):
    def __init__(self, params):
        # TODO create elliptical object
        super().__init__(params)


if __name__ == '__main__':
    # Quick test to ensure
    params = {
        'x_pixels': 128,
        'y_pixels': 128,
        'detector_distance': 6.0,
    }
    slicer = Slicer(params)
    mask = slicer.generate_standard_mask()
    ones = slicer.generate_ones_data()
    assert len(mask) == 128
    assert mask.shape == (128, 128)
    assert not np.all(mask == 1)
    assert len(ones) == 128
    assert ones.shape == (128, 128)
    assert np.all(ones == 1)

