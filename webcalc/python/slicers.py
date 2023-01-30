# TODO: Create slicer class and child slicers
# built-in imports
import math

import numpy as np
from scipy.special import gamma, gammainc


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
        nq = 0
        large_number = 1.0
        radius_center = 100
        data = self.intensity_2D
        data_i = []
        mask_i = []
        num_dimensions = 1
        center = 1
        x_indices = np.asarray(range(1, len(self.qx_values) + 1))
        y_indices = np.asarray(range(1, len(self.qy_values) + 1))
        x_distances = calculate_distance_from_beam_center(x_indices, self.x_center, self.pixel_size, self.coeff)
        y_distances = calculate_distance_from_beam_center(y_indices, self.y_center, self.pixel_size, self.coeff)
        total_distances = np.sqrt(x_distances * x_distances + y_distances * y_distances)
        num_dimensions = np.asarray([1 if total_distance > radius_center else 3 for total_distance in total_distances])
        center = np.asarray([1 if total_distance > radius_center else 2 for total_distance in total_distances])
        num_d_squared = num_dimensions * num_dimensions
        # FIXME: num_dimensions is an array...
        corrected_dx = x_distances + (np.asarray(list(range(1, num_dimensions + 1))) - center) * self.pixel_size / num_dimensions
        corrected_dy = y_distances + (
                    np.asarray(list(range(1, num_dimensions + 1))) - center) * self.pixel_size / num_dimensions
        i_radius = self.get_i_radius(corrected_dx, corrected_dy)
        nq = max(i_radius) if len(i_radius) > 0 else 0
        self.ave_intensity = np.zeros_like(list(np.asarray(range(nq))))
        self.d_sq = np.zeros_like(list(np.asarray(range(nq))))
        self.n_cells = np.zeros_like(list(np.asarray(range(nq))))
        # FIXME:
        for i in range(len(self.qx_values)):
            qx_val = self.qx_values[i]
            x_distence = self.calculate_distance_from_beam_center(i, "x")
            mask_i = self.mask[i]
            data_i = data[i]
            for j in range(len(self.qy_values)):
                qy_val = self.qy_values[j]
                if self.include_pixel(qx_val, qy_val, mask_i[j]):
                    y_distance = self.calculate_distance_from_beam_center(j, "y")
                    data_pixel = data_i[j]
                    total_distence = math.sqrt(x_distence * x_distence + y_distance * y_distance)
                    # breaks pixels up into a 3*3 grid close to beam center
                    if total_distence > radius_center:
                        num_dimensions = 1
                        center = 1
                    else:
                        num_dimensions = 3
                        center = 2
                    num_d_squared = num_dimensions * num_dimensions
                    # Loop over sliced pixels
                    for k in range(1, num_dimensions + 1):
                        corrected_dx = x_distence + (k - center) * self.pixel_size / num_dimensions
                        for l in range(1, num_dimensions + 1):
                            corrected_dy = y_distance + (l - center) * self.pixel_size / num_dimensions
                            i_radius = self.get_i_radius(corrected_dx, corrected_dy)
                            nq = i_radius if i_radius > nq else nq

                            # before reformated  self.ave_intensity[i_radius] = data_pixel/num_d_squared if self.ave_intensity[i_radius] is None else self.ave_intensity[i_radius]+data_pixel/num_d_squared
                            #                             self.d_sq[i_radius] = data_pixel*data_pixel/num_d_squared if self.d_sq[i_radius] is None else self.d_sq[i_radius]+data_pixel*data_pixel/num_d_squared
                            #                             self.n_cells[i_radius] = 1/num_d_squared if self.n_cells[i_radius] is None else self.n_cells[i_radius]+1 /num_d_squared
                            try:
                                self.ave_intensity[i_radius] = self.ave_intensity[i_radius] + data_pixel / num_d_squared
                            except IndexError:
                                print("Len one" + str(len(self.ave_intensity)))
                                self.ave_intensity.append(data_pixel / num_d_squared)
                                print("Len two" + str(len(self.ave_intensity)))
                            self.d_sq[i_radius] = data_pixel * data_pixel / num_d_squared if self.d_sq[
                                                                                                 i_radius] is None else \
                                self.d_sq[i_radius] + data_pixel * data_pixel / num_d_squared
                            self.n_cells[i_radius] = 1 / num_d_squared if self.n_cells[i_radius] is None else \
                                self.n_cells[i_radius] + 1 / num_d_squared
        for i in range(nq):
            self.calculate_q(i)
            if self.n_cells[i] <= 1:
                self.ave_intensity[i] = 0 if self.n_cells[i] == 0 or math.isnan(self.n_cells[i]) else \
                    self.ave_intensity[i] / self.n_cells[i]
                self.sigma_ave[i] = large_number
            else:
                self.ave_intensity[i] = self.ave_intensity[i] if math.isnan(self.n_cell[i]) else self.ave_intensity[i] / \
                                                                                                 self.n_cells[i]
                ave_sq = self.ave_intensity[i] * self.ave_intensity[i]
                ave_isq = self.d_sq[i] if math.isnan(self.n_cells[i]) else self.d_sq[i] / self.n_cells[i]
                diff = ave_isq - ave_sq
                self.sigma_ave[i] = large_number if diff < 0 else math.sqrt(diff / self.n_cells[i] - 1)
        self.calculate_resolution()

    def calculate_q(self, i):
        radius = (2 * i) * self.pixel_size / 2
        theta = math.atan(radius / self.SDD) / 2
        self.q_values[i] = (4 * math.pi / self.lambda_val) * math.sin(theta)

    def get_i_radius(self, x_val, y_val):
        return np.floor(np.sqrt(x_val * x_val + y_val * y_val) / self.pixel_size) + 1

    def calculate_resolution(self):
        velocity_neutron_1a = 3.956e5
        gravity_constant = 981.0
        small_number = 1e-10
        is_lenses = self.lens
        # Pixel size in mm
        pixel_size = self.pixel_size * 0.1
        # Base calculations
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
        var_gravity = 0.5 * gravity_constant * self.SDD*(self.SSD + self.SDD) / math.pow(velocity_neutron, 2)
        r_zero = self.SDD * np.tan(2.0 * np.asin(self.lambda_val * np.asarray(self.q_values) / (4.0 * np.pi)))
        delta = 0.5 * np.pow(self.beam_stop_size - r_zero, 2) / var_detector
        if r_zero < self.beam_stop_size:
            inc_gamma = np.exp(np.log(gamma(1.5))) * (1 - gammainc(1.5, delta) / gamma(1.5))
        else:
            inc_gamma = np.exp(np.log(gamma(1.5))) * (1 + gammainc(1.5, delta) / gamma(1.5))

        f_sub_s = 0.5 * (1.0 + np.erf((r_zero - self.beam_stop_size) / math.sqrt(2.0 * var_detector)))
        if f_sub_s < small_number:
            f_sub_s = small_number

        fr = 1.0 + np.sqrt(var_detector) * np.exp(-1.0 * delta) / r_zero * f_sub_s * np.sqrt(2.0 + np.pi)
        fv = inc_gamma / (f_sub_s * np.sqrt(math.pi)) - r_zero * r_zero * np.pow(fr - 1.0, 2) / var_detector
        rmd = fr + r_zero
        var_r1 = var_beam + var_detector * fv + var_gravity
        rm = rmd + 0.5 * var_r1 / rmd
        var_r = var_r1 - 0.5 * (var_r1 / rmd) * (var_r1 / rmd)
        if var_r < 0:
            var_r = 0.0
        self.q_average = (4.0 * np.pi / self.lambda_val) * np.sin(0.5 * np.atan(rm / self.SDD))
        self.sigma_q = self.q_average * np.sqrt((var_r / rmd) * (var_r / rmd) + var_lambda)
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
        # TODO fix calculate function so it does not have to be commented out
        # self.calculate()  # SCRR Why was this not here?

    def generate_ones_data(self) -> np.array:
        return np.ones((self.x_pixels, self.y_pixels))

    # Generate a standard SANS mask with the outer 2 pixels masked
    def generate_standard_mask(self):
        mask = [[1 if i <= 1 or i >= self.x_pixels - 2 or j <= 1 or j >= (self.y_pixels - 2) else 0
                 for i in range(self.x_pixels)] for j in range(self.y_pixels)]
        return np.asarray(mask)

    def include_pixel(self, x_val, y_val, mask):
        return mask == 0

    # Slicer recturn method for all the values need to return to slicer
    def slicer_return(self):
        # SCRR Return Method
        slicer_return = {}
        slicer_return["average_type"] = self.average_type
        return slicer_return


# Circular averaging class (No overridden methods)
class Circular(Slicer):
    def __init__(self, params):
        super().average_type = "circular"
        super().__init__(params)


# Sector averaging class 3 overridden methods
class Sector(Slicer):
    def __init__(self, params):
        super().average_type = "sector"
        super().__init__(params)

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
        super().average_type = "rectangular"
        super().__init__(params)

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
        super().average_type = "elliptical"
        super().__init__(params)

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
    mask = slicer.generate_standard_mask()
    ones = slicer.generate_ones_data()
    assert len(mask) == 128
    assert mask.shape == (128, 128)
    assert not np.all(mask == 1)
    assert len(ones) == 128
    assert ones.shape == (128, 128)
    assert np.all(ones == 1)
