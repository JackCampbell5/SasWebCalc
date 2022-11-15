# TODO: Create slicer class and child slicers
# QUESTION      Where is the object creation for this
import math


#  Calculate the x or y distance from the beam center of a given pixel
def calculate_distance_from_beam_center(pixel_value, pixel_center, pixel_size, coeff):
    return coeff * math.tan((pixel_value - pixel_center) * pixel_size / coeff)


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


def create_plot():
    return []


# Question are x_val and y-val needed in this method
def include_pixel(x_val, y_val, mask):
    return mask == 0


class Slicer:

    def __init__(self, params):

        # Import all parameters for slicer class

        # Params needed for calculate_q_range_slicer
        self.mask = 0.0
        self.intencity_2D = 0.0
        self.detector_distance = 0.0
        self.x_pixels = 0.0
        self.y_pixels = 0.0

        # Values are the default values
        # Q values
        self.qx_values = []
        self.qy_values = []
        self.q_values = [0]
        self.ave_intensity = [0]
        self.d_sq = [0]
        self.n_cells = [0]
        self.sigma_ave = [0]
        # Max and Min Q values
        self.max_qx = 0.0
        self.max_qy = 0.0
        self.min_qx = 0.0
        self.min_qy = 0.0

        # Averaging Parameters
        self.detector_sections = 'both'
        self.phi = 0.0
        self.d_phi = math.pi / 2
        self.q_center = 0.0
        self.q_width = 0.3
        self.aspect_ratio = 1.0

        # Instrumental Parameters
        self.lambda_val = 6.0
        self.lambda_width = 0.14
        self.guides = 0.0
        self.source_aperture = 25.4
        self.sample_aperture = 6.35
        self.aperture_offset = 5.00
        self.beam_stop_size = 5.08
        self.SSD = 1627
        self.SDD = 1530
        self.pixel_size = 5.08
        self.coeff = 10000
        self.x_center = 64.5
        self.y_center = 64.5

        # Calculate parameters
        self.phi_upper = 0.0
        self.phi_lower = 0.0
        self.phi_x = 0.0
        self.phi_y = 0.0
        self.phi_to_ur_corner = 0.0
        self.phi_to_ul_corner = 0.0
        self.phi_to_ll_corner = 0.0
        self.phi_to_lr_corner = 0.0

        # set params
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
        data = self.intencity_2D
        data_i = []
        mask_i = []
        num_dimensions = 1
        center = 1
        for i in range(self.qx_values):
            qx_val = self.qx_values[i]
            x_distence = self.calculate_distence_from_beam_center(i, "x")
            mask_i = self.mask[i]
            data_i = data[i]
            for j in range(self.qy_values):
                qy_val = self.qy_values[j]
                if include_pixel(qx_val, qy_val, mask_i[j]):
                    y_distance = calculate_distance_from_beam_center(j, "y")
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
                            self.ave_intensity[i_radius] = data_pixel / num_d_squared if self.ave_intensity[
                                                                                             i_radius] is None else \
                            self.ave_intensity[i_radius] + data_pixel / num_d_squared
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
            if self.q_values[i] > 0.0:
                self.calculate_resolution(i)

    def calculate_q(self, i):
        radius = (2 * i) * self.pixel_size / 2
        theta = math.atan(radius / self.SDD) / 2
        self.q_values[i] = (4 * math.pi / self.lambda_val) * math.sin(theta)

    def get_i_radius(self, x_val, y_val):
        return math.floor(math.sqrt(x_val * x_val + y_val * y_val) / self.pixel_size) + 1

    def calculate_resolution(self, i):
        pass

    def calculate_distance_from_beam_center(self, pixel_value, x_or_y):
        if x_or_y.lower() == "x":
            pixel_center = self.x_center
        else:
            pixel_center = self.y_center
        return self.coeff * math.tan(pixel_value - pixel_center) * self.pixel_size / self.coeff

    # Calculate Q Range Slicer and its helper methods
    def calculate_q_range_slicer(self):
        # Detector values pixel size in mm
        self.intencity_2D = self.generate_ones_data()
        self.mask = self.generate_standard_mask()
        # Calculate Qx and Qy values
        for i in range(self.x_pixels):
            x_distance = calculate_distance_from_beam_center(i, self.x_center, self.pixel_size, self.coeff)
            thetaX = math.atan(x_distance / self.detector_distance) / 2
            self.qx_values.append((4 * math.pi / self.lambda_val) * math.sin(thetaX))
        for j in range(self.y_pixels):
            y_distence = calculate_distance_from_beam_center(i, self.y_center, self.pixel_size, self.coeff)
            thetaY = math.atan(y_distence / self.detector_distance) / 2
            self.qy_values.append((4 * math.pi / self.lambda_val) * math.sin(thetaY))

    def generate_ones_data(self):
        data = []
        dataY = []
        for i in range(self.x_pixels):
            for j in range(self.y_pixels):
                dataY.append(1)
            data.append(dataY)
        return data

    # Generate a standard SANS mask with the outer 2 pixels masked
    def generate_standard_mask(self):
        mask = []
        for i in range(self.x_pixels):
            mask_inset = []
            for j in range(self.y_pixels):
                if i <= 1 or i >= self.x_pixels - 2:
                    # Top and bottom of the 2 pixels should be masked
                    mask_inset.append(1)
                elif j <= 1 or j >= (self.y_pixels - 2):
                    # Left and right 2 pixels should be masked
                    mask_inset.append(1)
                else:
                    # Remainder should not be masked
                    mask_inset.append(0)
            mask.append(mask_inset)
        return mask


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
