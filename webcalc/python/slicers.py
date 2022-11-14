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
        # Max and Min Q values
        self.maxQx = 0.0
        self.maxQy = 0.0
        self.minQx = 0.0
        self.minQy = 0.0

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

        # set params
        set_params(self, params)
        self.set_values()

    def set_values(self):
        # Sets the max and min q values and all the phi values

        # Min and max Q value
        self.maxQx = 0.3 if max(self.qx_values) is None else max(self.qx_values)
        self.maxQy = 0.3 if max(self.qy_values) is None else max(self.qy_values)
        self.minQx = 0.0 if min(self.qx_values) is None else min(self.qx_values)
        self.minQy = 0.0 if min(self.qy_values) is None else min(self.qy_values)

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
