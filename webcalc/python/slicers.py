# TODO: Create slicer class and child slicers
# built-in imports
import math
from typing import Union

import numpy as np
from scipy.special import gamma, gammainc, erf


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
            if value is not None:
                setattr(instance, key, value)
        else:
            # Print unrecognized attributes to the console
            print(f"The parameter {key} is not a known {instance} attribute. Unable to set it to {value}.")


def add_at_location(array, location):
    pass


class Slicer:

    def __init__(self, params):

        # Import all parameters for slicer class

        self.average_type = "Default"

        # Params needed for calculate_q_range_slicer
        self.mask: np.array = np.zeros_like(0)
        self.intensity_2D: np.array = np.zeros_like(0)
        self.detector_distance: float = 0.0
        self.x_pixels: int = 0
        self.y_pixels: int = 0

        # Values are the default values
        # Q values
        self.qx_values = None
        self.qy_values = None
        self.q_values = None
        self.ave_intensity = None
        self.d_sq = [0]
        self.n_cells = [0]
        self.sigma_ave = [0]
        self.q_average = [0]
        self.sigma_q = [0]
        self.f_subs = [0]
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
        self.lens = False
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
        self.max_qx = 0.3 if len(self.qx_values) == 0 else max(self.qx_values)
        self.max_qy = 0.3 if len(self.qy_values) == 0 else max(self.qy_values)
        self.min_qx = 0.0 if len(self.qx_values) == 0 else min(self.qx_values)
        self.min_qy = 0.0 if len(self.qy_values) == 0 else min(self.qy_values)

        # Calculated parameters
        self.phi_upper = self.phi * self.d_phi
        self.phi_lower = self.phi - self.d_phi
        self.phi_x = math.cos(self.phi)
        self.phi_y = math.sin(self.phi)
        self.phi_to_ur_corner = math.atan(self.max_qy / self.max_qx)
        self.phi_to_ul_corner = math.atan(self.max_qy / self.min_qx) + math.pi
        self.phi_to_ll_corner = math.atan(self.min_qy / self.min_qx) + math.pi
        self.phi_to_lr_corner = math.atan(self.min_qy / self.max_qx) + 2 * math.pi

    def calculate(self):
        """Calculate the average intensity for all Q values at a given instrument configuration"""
        large_number = 1.0
        # The radius, in cm, from the center of the beam to slice pixels into a 3x3 grid
        radius_center = 100
        # Number of unique Q points used for the averaging
        nq = 0
        # x and y pixel indices
        x_indices = np.asarray(range(1, len(self.qx_values) + 1))
        y_indices = np.asarray(range(1, len(self.qy_values) + 1))
        # Calculate distance array from the beam center
        x_distances = np.full((self.x_pixels, self.x_pixels),
                              calculate_distance_from_beam_center(x_indices, self.x_center, self.pixel_size,
                                                                  self.coeff))
        y_distances = np.full((self.y_pixels, self.y_pixels),
                              calculate_distance_from_beam_center(y_indices, self.y_center, self.pixel_size,
                                                                  self.coeff))
        # Calculate total distances for all pixels
        total_distances = np.sqrt(x_distances * x_distances + y_distances * y_distances)
        # Convert pixels near the center into 3x3 pixels
        num_dimensions = np.ones(np.shape(total_distances))
        num_dimensions[total_distances <= radius_center] = 3
        # Set existing pixel center value
        center = np.ones(np.shape(total_distances))
        center[total_distances <= radius_center] = 2
        num_d_squared = num_dimensions * num_dimensions
        self.ave_intensity = np.zeros(1000)
        self.d_sq = np.zeros(1000)
        self.n_cells = np.zeros(1000)

        for i in range(self.x_pixels):
            for j in range(self.y_pixels):
                data_px = self.intensity_2D[i][j]
                nd = int(num_dimensions[i][j])
                for k in range(1, nd):
                    corrected_dx = x_distances[i][j] + (k - center[i][j]) * self.pixel_size / k
                    n_d_sqr = nd
                    for el in range(1, nd):
                        corrected_dy = y_distances[i][j] + (el - center[i][j]) * self.pixel_size / el
                        i_radius = self.get_i_radius(corrected_dx, corrected_dy)
                        self.n_cells[i_radius] += 1 / n_d_sqr
                        self.ave_intensity[i_radius] = (0 if self.n_cells[i] == 0 or math.isnan(self.n_cells[i])
                                                        else self.ave_intensity[i] / self.n_cells[i])
                        self.d_sq[i_radius] += data_px * data_px / n_d_sqr
                        nq = max(i_radius, nq)

        self.ave_intensity = self.ave_intensity[:nq]
        self.d_sq = self.d_sq[:nq]
        self.n_cells = self.n_cells[:nq]
        nq_array = np.arange(nq)
        self.calculate_q(nq_array)
        ave_sq = self.ave_intensity * self.ave_intensity
        ave_isq = np.asarray([self.d_sq[i] if np.isnan(self.n_cells[i]) else self.d_sq[i] / self.n_cells[i]
                              for i in nq_array])
        diff = ave_isq - ave_sq
        self.sigma_ave = np.asarray([large_number if diff[i] < 0 or self.n_cells[i] <= 1
                                     else math.sqrt(diff[i] / (self.n_cells[i] - 1)) for i in nq_array])
        self.calculate_resolution()

    def calculate_q(self, i: Union[np.ndarray, int]):
        """Calculates the q value for a given detector pixel, i pixels from the center of the beam or a range of
        q values if i is ann array

        Args:
            i: Either an integer or an array of integers
        """
        radius = i * self.pixel_size
        theta = np.arctan(radius / self.SDD) / 2
        if isinstance(i, (np.ndarray, np.generic)):
            self.q_values = (4 * np.pi / self.lambda_val) * np.sin(theta)
        else:
            self.q_values[i] = (4 * np.pi / self.lambda_val) * np.sin(theta)

    def get_i_radius(self, x_val, y_val):
        return int(np.floor(np.sqrt(x_val * x_val + y_val * y_val) / self.pixel_size) + 1)

    def calculate_resolution(self):
        velocity_neutron_1a = 3.956e5
        gravity_constant = 981.0
        small_number = 1e-10
        is_lenses = self.lens
        # Pixel size in mm
        pixel_size = self.pixel_size * 0.1
        # Base calculations
        # self.ssd is the issue
        lp = 1 / (1 / self.SDD + 1 / self.SSD)
        # Calculate variance
        var_lambda = self.lambda_width * self.lambda_width / 6.0
        if is_lenses:
            var_beam = 0.25 * math.pow(self.source_aperture * self.SDD / self.SSD, 2) + 0.25 * (2 / 3) * math.pow(
                self.lambda_width / self.lambda_val, 2) * math.pow(self.sample_aperture * self.SDD / lp, 2)
        else:
            var_beam = 0.25 * math.pow(self.source_aperture * self.SDD / self.SSD, 2) + 0.25 * math.pow(
                self.sample_aperture * self.SDD / lp, 2)
        var_detector = math.pow(pixel_size / 2.3548, 2) + (pixel_size + pixel_size) / 12
        velocity_neutron = velocity_neutron_1a / self.lambda_val
        var_gravity = 0.5 * gravity_constant * self.SDD * (self.SSD + self.SDD) / math.pow(velocity_neutron, 2)
        r_zero = self.SDD * np.tan(2.0 * np.arcsin(self.lambda_val * np.asarray(self.q_values) / (4.0 * np.pi)))
        delta = 0.5 * np.power(self.beam_stop_size - r_zero, 2) / var_detector
        inc_gamma = np.full_like(r_zero, np.exp(np.log(gamma(1.5))) * (1 + gammainc(1.5, delta) / gamma(1.5)))
        # FIXME: indexing broken here
        # inc_gamma[r_zero < self.beam_stop_size] = np.exp(np.log(gamma(1.5))) * (1 - gammainc(1.5, delta) / gamma(1.5))
        # FIXME AS ERF OUTPUTS ARRAy
        f_sub_s = 0.5 * (1.0 + erf((r_zero - self.beam_stop_size) / math.sqrt(2.0 * var_detector)))
        f_sub_s[f_sub_s < small_number] = small_number
        fr = 1.0 + np.sqrt(var_detector) * np.exp(-1.0 * delta) / r_zero * f_sub_s * np.sqrt(2.0 + np.pi)
        fv = inc_gamma / (f_sub_s * np.sqrt(math.pi)) - r_zero * r_zero * np.power(fr - 1.0, 2) / var_detector
        rmd = fr + r_zero
        var_r1 = var_beam + var_detector * fv + var_gravity
        rm = rmd + 0.5 * var_r1 / rmd
        var_r = var_r1 - 0.5 * (var_r1 / rmd) * (var_r1 / rmd)
        var_r[var_r < 0] = 0.0
        self.q_average = (4.0 * np.pi / self.lambda_val) * np.sin(0.5 * np.arctan(rm / self.SDD))
        print(type(self.q_average[1]))
        print(np.isnan(self.q_average[0]))
        if np.isnan(self.q_average[0]): self.q_average[0] = 0.0
        self.sigma_q = self.q_average * np.sqrt((var_r / rmd) * (var_r / rmd) + var_lambda)
        if np.isnan(self.sigma_q[0]): self.sigma_q[0] = 0.0
        self.f_subs = f_sub_s

    def calculate_distance_from_beam_center(self, pixel_value, x_or_y):
        if x_or_y.lower() == "x":
            pixel_center = self.x_center
        else:
            pixel_center = self.y_center
        return self.coeff * math.tan(pixel_value - pixel_center) * self.pixel_size / self.coeff

    # Calculate Q Range Slicer and its helper methods
    def calculate_q_range_slicer(self):
        # Detector values pixel size in mm
        self.generate_ones_data()
        self.generate_standard_mask()
        # Calculate Qx and Qy values
        x_pixels = np.array([i for i in range(self.x_pixels)])
        x_distances = calculate_distance_from_beam_center(x_pixels, self.x_center, self.pixel_size, self.coeff)
        theta_x = np.arctan(x_distances / (self.detector_distance*10)) / 2
        self.qx_values = (4 * math.pi / self.lambda_val) * np.sin(theta_x)
        y_pixels = np.array([i for i in range(self.y_pixels)])
        y_distances = calculate_distance_from_beam_center(y_pixels, self.y_center, self.pixel_size, self.coeff)
        theta_y = np.arctan(y_distances / (self.detector_distance*10)) / 2
        self.qy_values = (4 * math.pi / self.lambda_val) * np.sin(theta_y)
        self.calculate()

    def generate_ones_data(self):
        """Create an array of 1s as a basis for the 2D intensity values. These 1s willed be scaled relative to the
        average intensity for each pixel"""
        self.intensity_2D = np.ones((self.x_pixels, self.y_pixels))

    def generate_standard_mask(self):
        """ Generate an array that uses 1 to represent a masked pixel and 0 otherwise. The outer two pixels are masked
        by default."""
        self.mask = [[1 if i <= 1 or i >= self.x_pixels - 2 or j <= 1 or j >= (self.y_pixels - 2) else 0
                      for i in range(self.x_pixels)] for j in range(self.y_pixels)]

    def include_pixel(self, x_val, y_val, mask):
        return mask == 0

    # Slicer recturn method for all the values need to return to slicer
    def slicer_return(self):
        slicer_return = {}
        slicer_return["averageType"] = self.average_type
        slicer_return["detectorSections"] = self.detector_sections
        slicer_return["phi"] = self.phi
        slicer_return["phiUpper"] = self.phi_upper
        slicer_return["phiUpper"] = self.phi_lower
        slicer_return["phiToURCorner"] = self.phi_to_ur_corner
        slicer_return["phiToURCorner"] = self.phi_to_ul_corner
        slicer_return["phiToLLCorner"] = self.phi_to_ll_corner
        slicer_return["phiToLRCorner"] = self.phi_to_lr_corner
        slicer_return["maxQx"] = self.max_qx
        slicer_return["maxQy"] = self.max_qy
        slicer_return["minQx"] = self.min_qy
        slicer_return["minQx"] = self.min_qx
        slicer_return["qWidth"] = self.q_width
        return slicer_return


# Circular averaging class (No overridden methods)
class Circular(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "circular"


# Sector averaging class 3 overridden methods
class Sector(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "sector"

    def include_pixel(self, x_val, y_val, mask):
        # Overriding does work
        pixel_angle = math.atan(x_val / y_val)
        is_correct_angle = (pixel_angle > self.phi_lower) and (pixel_angle < self.phi_upper)
        forward = is_correct_angle and x_val > 0
        mirror = is_correct_angle and x_val < 0
        both = self.detector_sections == "both" and (mirror or forward)
        left = self.detector_sections == "left" and mirror
        right = self.detector_sections == "right" and forward
        return (both or left or right) and (mask == 0)


class Rectangular(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "rectangular"

    def include_pixel(self, x_val, y_val, mask):
        corrected_radius = math.sqrt(x_val * x_val + y_val * y_val)
        dot_product = (x_val * self.phi_x + y_val * self.phi_y) / corrected_radius
        dphi_pixel = math.acos(dot_product)
        d_perpendicular = corrected_radius * math.sin(dphi_pixel)
        a = (d_perpendicular <= 0.5 * self.q_width * self.pixel_size)
        b = self.detector_sections == "both"
        c = self.detector_sections == "left" and dot_product >= 0
        d = self.detector_sections == "right" and dot_product < 0
        return a and (b or c or d) and (mask == 0)


class Elliptical(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "elliptical"

    def calculate_q(self, theta):
        # FIXME: This needs to know the pixel position
        return super().calculate_q(theta)

    def calculate_radius(self, x_val, y_val):
        # Supposed to be super().calculate _radius but DNE in slicer class
        i_circular = super().get_i_radius(x_val, y_val)
        rho = math.atan(x_val / y_val) - self.phi
        return math.floor(i_circular * math.sqrt(
            math.cos(rho) * math.cos(rho) + self.aspect_ratio * math.sin(rho) * math.sin(rho))) + 1


if __name__ == '__main__':
    # Quick test to ensure
    params = {
        'x_pixels': 128,
        'y_pixels': 128,
        'detector_distance': 6.0,
    }
    slicer = Slicer(params)
    slicer.generate_standard_mask()
    slicer.generate_ones_data()
    assert len(slicer.mask) == 128
    assert slicer.mask.shape == (128, 128)
    assert not np.all(slicer.mask == 1)
    assert len(slicer.intensity_2D) == 128
    assert slicer.intensity_2D.shape == (128, 128)
    assert np.all(slicer.intensity_2D == 1)
