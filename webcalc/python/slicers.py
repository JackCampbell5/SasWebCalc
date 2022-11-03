# TODO: Create slicer class and child slicers
# QUESTION      Where is the object creation for this
from .instrument import set_params


class Slicer:

    def __init__(self, params):
        self.x_pixels = 0.0
        self.y_Pixels = 0.0
        self.x_center = 0.0
        self.y_center = 0.0
        self.pixel_size = 0.0
        self.coeff = 0.0
        self.lamda = 0.0
        self.aperture_offset = 0.0
        self.detector_distance = 0.0

        set_params(params)

    def calculate_q_range_slicer(self, index):
        pass


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
