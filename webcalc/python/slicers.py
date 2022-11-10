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


class Slicer:

    def __init__(self, params):

        # Import all parameters for slicer class
        self.mask = 0.0
        self.intencity_2D = 0.0
        self.phi = 0.0
        self.d_phi = 0.0
        self.detector_sections = 0.0
        self.q_center = 0.0
        self.q_width = 0.0
        self.aspect_ratio = 0.0
        self.x_center = 0.0
        self.y_center = 0.0
        self.pixel_size = 0.0
        self.lambda_val = 0.0
        self.detector_distance = 0.0
        self.lambda_width = 0.0
        self.guides = 0.0
        self.source_aperture = 0.0
        self.sample_aperture = 0.0
        self.beam_stop_size = 0.0
        self.SSD = 0.0
        self.SDD = 0.0
        self.aperture_offset = 0.0
        self.coeff = 0.0
        self.x_pixels = 0.0
        self.y_pixels = 0.0
        self.qx_values = []
        self.qy_values = []
        # set params
        set_params(self, params)

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
            self.qy_values = (4 * math.pi / self.lambda_val) * math.sin(thetaY)

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
