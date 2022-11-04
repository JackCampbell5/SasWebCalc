# TODO: Create slicer class and child slicers
# QUESTION      Where is the object creation for this
import math


#  Calculate the x or y distance from the beam center of a given pixel
def calculate_distance_from_beam_center(pixel_value, pixel_center, pixel_size, coeff):
    return coeff * math.tan((pixel_value - pixel_center) * pixel_size / coeff)


class Slicer:

    def __init__(self, params):

        # Import parameters needed for calculate Q range slicer
        self.x_pixels = 0.0
        self.y_Pixels = 0.0
        self.x_center = 0.0
        self.y_center = 0.0
        self.pixel_size = 0.0
        self.coeff = 0.0
        self.lamda = 0.0
        self.aperture_offset = 0.0
        self.detector_distance = 0.0
        self.qx_values = []
        self.qy_values = []
        self.averaging_params = []
        # set params functions
        # Run calculate Q range slicer
        params = self.calculate_q_range_slicer()
        # Constructor params from slicer class

        # set params a second time

        # TODO   FIX
        # set_params(params)

    def calculate_q_range_slicer(self):
        # Detector values pixel size in mm
        self.intencity_2D = self.generate_ones_data()
        self.mask = self.generate_standard_mask()

        # Calculate Qx and Qy values
        for i in self.x_pixels:
            x_distance = calculate_distance_from_beam_center(i, self.x_center, self.pixel_size, self.coeff)
            thetaX = math.atan(x_distance / self.detector_distance) / 2
            self.qx_values[i] = (4 * math.pi / self.lamda) * math.sin(thetaX)
        for j in self.y_Pixels:
            y_distence = calculate_distance_from_beam_center(i, self.y_center, self.pixel_size, self.coeff)
            thetaY = math.atan(y_distence / self.detector_distance) / 2
            self.qy_values = (4 * math.pi / self.lamda) * math.sin(thetaY)

        averaging_params = self.averaging_params
        updatedParams = {}
        updatedParams["phi"] = (math.pi/180)*averaging_params[0]
        updatedParams["dPhi"] = (math.pi/180)*averaging_params[1]
        updatedParams["detector_sections"] = averaging_params[2]
        updatedParams["q_center"] = averaging_params[3]
        updatedParams["q_width"] = averaging_params[4]
        updatedParams["aspectratio"] = averaging_params[5]


        #  Generate a data set of all ones for a given detector
        # create params array
        params = []
        return params;

    def generate_ones_data(self):
        data = []
        dataY = []
        for i in self.x_pixels:
            for j in self.y_Pixels:
                dataY[j] = 1
            data[i] = dataY;
        return data

    # Generate a standard SANS mask with the outer 2 pixels masked
    def generate_standard_mask(self):
        mask = []
        for i in self.x_pixels:
            mask_inset = []
            for j in self.y_Pixels:
                if i <= 1 or i >= self.x_pixels - 2:
                    # Top and bottom of the 2 pixels should be masked
                    mask_inset[j] = 1
                elif j <= 1 or j >= (self.y_Pixels - 2):
                    # Left and right 2 pixels should be masked
                    mask_inset[j] = 1
                else:
                    # Remainder should not be masked
                    mask_inset[j] = 0
            mask[i] = mask_inset
        return mask


class Circular:
    def __init__(self, parent, params):
        super().__init__(self, params)


class Sector:
    def __init__(self, parent, params):
        print(self)


class Rectangular:
    def __init__(self, parent, params):
        print(self)


class Elliptical:
    def __init__(self, parent, params):
        # TODO create elliptical object
        print(self)
