import numpy as np
from scipy.special import gamma, gammainc, erf

VALUE_TYPE = str | float | int


def calculate_distance_from_beam_center(
        pixel_value: float | np.ndarray,
        pixel_center: float,
        pixel_size: float,
        coeff: float) -> float:
    """Calculate the x or y distance from the beam center of a given pixel"""
    if isinstance(pixel_value, np.ndarray):
        pixel_center = np.full(pixel_value.shape, pixel_center)
    return coeff * np.tan((pixel_value - pixel_center) * pixel_size / coeff)


def set_params(instance: object, params: dict[str, VALUE_TYPE]):
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

    def __init__(self, params: dict[str, VALUE_TYPE]):

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
        self.q_2d_values = None
        self.qx_2d_values = None
        self.qy_2d_values = None
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
        self.d_phi: float = np.pi / 2
        self.q_center: float = 0.0
        self.q_width: float = 0.3
        self.aspect_ratio: float = 1.0

        # Instrumental Parameters
        self.lambda_val: float = 6.0
        self.lambda_width: float = 0.14  # Fractional wavelength spread (FWHM), e.g. 0.14 for 14%
        self.guides: int = 0
        self.lens = False
        # All lengths in cm. Apertures are radii, the beam stop size is a diameter.
        self.source_aperture: float = 2.54
        self.sample_aperture: float = 0.635
        self.aperture_offset: float = 5.00
        self.beam_stop_size: float = 5.08
        # Detector spatial resolution (FWHM) in cm - 0.5 cm for the Ordela detectors (Igor: DDet)
        self.detector_resolution: float = 0.5
        # Annulus width in pixels (Igor: gBinWidth)
        self.bin_width: float = 1.0
        self.SSD: float = 1627
        self.SDD: float = 1530
        self.pixel_size = 0.508
        # Pixel sizes along x and y in cm. If not given they default to pixel_size (set after params are loaded).
        self.pixel_size_x = None
        self.pixel_size_y = None
        self.coeff: float = 10000
        self.x_center: float = 64.5
        self.y_center: float = 64.5
        # Optional pixel positions (cm) relative to the beam center, one per pixel along x and along y. When given,
        # they are used instead of the beam center/pixel size/coeff calculation (e.g. VSANS tube panels).
        self.x_positions = None
        self.y_positions = None

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
        set_params(self, params)
        self.validate_geometry()
        # The angular values are needed by include_pixel() during the average, so set them first
        self.set_angular_values()
        self.calculate_q_range_slicer()
        self.set_values()

    def validate_geometry(self):
        """Fill in derived pixel sizes and fail early with a clear message on unusable detector geometry."""
        if not self.pixel_size_x:
            self.pixel_size_x = self.pixel_size
        if not self.pixel_size_y:
            self.pixel_size_y = self.pixel_size
        if not self.pixel_size:
            self.pixel_size = (self.pixel_size_x + self.pixel_size_y) / 2.0
        if not self.pixel_size or self.pixel_size <= 0 or self.pixel_size_x <= 0 or self.pixel_size_y <= 0:
            raise ValueError(f"Slicer pixel sizes must be > 0 cm (pixel_size={self.pixel_size}, "
                             f"pixel_size_x={self.pixel_size_x}, pixel_size_y={self.pixel_size_y}).")
        if not self.x_pixels or not self.y_pixels:
            raise ValueError(f"Slicer needs the number of pixels (x_pixels={self.x_pixels}, y_pixels={self.y_pixels}).")
        self.x_pixels = int(self.x_pixels)
        self.y_pixels = int(self.y_pixels)
        for name, n in (('x_positions', self.x_pixels), ('y_positions', self.y_pixels)):
            value = getattr(self, name)
            if value is not None and len(value) != n:
                raise ValueError(f"{name} has {len(value)} entries but the detector has {n} pixels.")

    def pixel_distances(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns the x and y distances (cm) of each pixel column/row from the beam center."""
        if self.x_positions is not None:
            x_dist = np.asarray(self.x_positions, dtype=float)
        else:
            # 1-based pixel numbers, like Igor
            x_dist = calculate_distance_from_beam_center(
                np.arange(1, self.x_pixels + 1, dtype=float), self.x_center, self.pixel_size_x, self.coeff)
        if self.y_positions is not None:
            y_dist = np.asarray(self.y_positions, dtype=float)
        else:
            y_dist = calculate_distance_from_beam_center(
                np.arange(1, self.y_pixels + 1, dtype=float), self.y_center, self.pixel_size_y, self.coeff)
        return x_dist, y_dist

    def set_angular_values(self):
        """Defines the sector/rectangle angles used to select pixels while averaging."""
        self.phi_upper = self.phi + self.d_phi
        self.phi_lower = self.phi - self.d_phi
        self.phi_x = np.cos(self.phi)
        self.phi_y = np.sin(self.phi)

    def set_values(self):
        """Defines derived and calculated values based on the values passed to the class."""
        MIN_Q = 1.0e-7

        # Min and max Q value
        self.max_qx = 0.3 if len(self.qx_values) == 0 else max(self.qx_values)
        self.max_qy = 0.3 if len(self.qy_values) == 0 else max(self.qy_values)
        self.min_qx = MIN_Q if len(self.qx_values) == 0 else min(self.qx_values)
        self.min_qy = MIN_Q if len(self.qy_values) == 0 else min(self.qy_values)

        # Calculated parameters
        self.set_angular_values()
        self.phi_to_ur_corner = np.atan(self.max_qy / self.max_qx)
        self.phi_to_ul_corner = np.atan(self.max_qy / self.min_qx) + np.pi
        self.phi_to_ll_corner = np.atan(self.min_qy / self.min_qx) + np.pi
        self.phi_to_lr_corner = np.atan(self.min_qy / self.max_qx) + 2 * np.pi

    def calculate(self):
        """Calculate the average intensity for all Q values at a given instrument configuration.

        Port of S_CircularAverageTo1D / S_IncrementPixel from SASCALC.ipf. All lengths are in cm.
        """
        # Error value used when an error can't be estimated (Igor uses 1, not 1e10, so it plots sensibly)
        large_number = 1.0
        # Pixels within this radius (cm) of the beam center are split into a 3x3 grid (Igor: 100 mm)
        radius_center = 10.0

        pixel_size_x = self.pixel_size_x
        pixel_size_y = self.pixel_size_y
        ddr = self.bin_width * self.pixel_size  # Annulus width in cm

        # Distance of every pixel from the beam center.
        # x varies along axis 0 and y varies along axis 1 so that [i][j] is pixel (x_i, y_j).
        x_dist, y_dist = self.pixel_distances()
        x_distances, y_distances = np.meshgrid(x_dist, y_dist, indexing='ij')
        split_pixel = np.hypot(x_distances, y_distances) <= radius_center

        unmasked = np.asarray(self.mask) == 0
        data = np.asarray(self.intensity_2D, dtype=float)

        # Accumulators - sized to hold every possible annulus on the detector
        n_bins = int(np.ceil(np.hypot(np.max(np.abs(x_dist)), np.max(np.abs(y_dist))) / ddr)) + 3
        ave_intensity = np.zeros(n_bins)
        d_sq = np.zeros(n_bins)
        n_cells = np.zeros(n_bins)

        # (split?, nd, fd): whole pixels are used as-is, pixels near the beam center are broken into 9 parts
        for is_split, nd, fd in ((False, 1, 1), (True, 3, 2)):
            selected = unmasked & (split_pixel == is_split)
            if not np.any(selected):
                continue
            data_px = data[selected]
            dx = x_distances[selected]
            dy = y_distances[selected]
            weight = 1.0 / (nd * nd)
            for ll in range(1, nd + 1):
                dxx = dx + (ll - fd) * pixel_size_x / 3
                for kk in range(1, nd + 1):
                    dyy = dy + (kk - fd) * pixel_size_y / 3
                    # Mask has already been applied, so pass an all-zero mask to the selection method
                    keep = np.broadcast_to(
                        np.asarray(self.include_pixel(dxx, dyy, np.zeros_like(dxx)), dtype=bool), dxx.shape)
                    if not np.any(keep):
                        continue
                    i_radius = self.get_i_radius(dxx[keep], dyy[keep])
                    np.add.at(ave_intensity, i_radius, data_px[keep] * weight)
                    np.add.at(d_sq, i_radius, data_px[keep] * data_px[keep] * weight)
                    np.add.at(n_cells, i_radius, weight)

        # Keep only annuli that contain pixels (panels away from the beam center have no inner annuli)
        filled = np.nonzero(n_cells)[0]
        ave_intensity = ave_intensity[filled]
        self.d_sq = d_sq[filled]
        self.n_cells = n_cells[filled]

        with np.errstate(divide='ignore', invalid='ignore'):
            self.ave_intensity = np.where(self.n_cells > 0, ave_intensity / self.n_cells, 0.0)
            ave_isq = np.where(self.n_cells > 0, self.d_sq / self.n_cells, 0.0)
            diff = ave_isq - self.ave_intensity * self.ave_intensity
            self.sigma_ave = np.where((self.n_cells > 1) & (diff > 0),
                                      np.sqrt(diff / (self.n_cells - 1)), large_number)

        self.calculate_q(filled)
        self.calculate_resolution()

    def calculate_q(self, i: np.ndarray | int):
        """Calculates the q value at the center of annulus i (0-based) or a range of q values if i is an array

        Args:
            i: Either an integer or an array of integers
        """
        # Bin center, Igor: rr = (2*kk-1)*ddr/2 with 1-based kk
        radius = (np.asarray(i) + 0.5) * self.bin_width * self.pixel_size
        theta = np.arctan(radius / self.SDD) / 2
        q = (4 * np.pi / self.lambda_val) * np.sin(theta)
        if isinstance(i, (np.ndarray, np.generic)):
            self.q_values = q
        else:
            self.q_values[i] = q

    def get_i_radius(self, x_val, y_val):
        """Returns the 0-based annulus index for a position (equivalent to Igor's ir - 1)"""
        if not self.pixel_size:
            self.pixel_size = (self.pixel_size_x + self.pixel_size_y) / 2.0
        ddr = self.bin_width * self.pixel_size
        return np.floor(np.sqrt(x_val * x_val + y_val * y_val) / ddr).astype(int)

    def calculate_resolution(self):
        """Calculates sigma Q, Q bar, and the beam stop shadow factor for every q value.

        Port of S_getResolution from SASCALC.ipf (JGB = Barker & Pedersen, J. Appl. Cryst. 28, 105 (1995)).
        All lengths are in cm. Apertures are radii, the beam stop size is a diameter, and the wavelength
        spread is fractional (FWHM).
        """
        velocity_neutron_1a = 3.956e5  # Velocity [cm/s] of a 1 A neutron
        gravity_constant = 981.0  # [cm/s^2]
        small_number = 1e-10
        # Base values
        lambda_val = self.lambda_val
        lambda_width = self.lambda_width  # Fractional FWHM (param_restructure already divides the % by 100)
        l1 = self.SSD  # Source aperture to sample aperture
        # Sample aperture to detector (Igor: L2 = SDD + apOff)
        l2 = self.detector_distance if self.detector_distance else self.SDD + self.aperture_offset
        s1 = self.source_aperture  # Source aperture radius
        s2 = self.sample_aperture  # Sample aperture radius
        bs = 0.5 * self.beam_stop_size  # Beam stop radius
        del_r = self.bin_width * self.pixel_size  # Annulus width
        lp = 1 / (1 / l2 + 1 / l1)
        # Calculate variances
        var_lambda = lambda_width * lambda_width / 6.0
        if self.lens:
            # JGB eq (6) and eq (20) from Mildner paper
            var_beam = 0.25 * np.pow(s1 * l2 / l1, 2) + 0.25 * (2. / 3.) * lambda_width ** 2 * np.pow(s2 * l2 / lp, 2)
        else:
            var_beam = 0.25 * np.pow(s1 * l2 / l1, 2) + 0.25 * np.pow(s2 * l2 / lp, 2)
        # JGB eq (7) - 2.3548 converts the detector FWHM to a Gaussian sigma
        var_detector = np.pow(self.detector_resolution / 2.3548, 2) + (del_r * del_r) / 12.0
        velocity_neutron = velocity_neutron_1a / lambda_val
        y_gravity = 0.5 * gravity_constant * l2 * (l1 + l2) / np.pow(velocity_neutron, 2)  # JGB eq (8)
        var_gravity = 2.0 * var_lambda * y_gravity * y_gravity  # JGB eq (9), 2022 form
        r_zero = l2 * np.tan(2.0 * np.arcsin(lambda_val * np.asarray(self.q_values, dtype=float) / (4.0 * np.pi)))
        r_zero = np.where(r_zero < small_number, small_number, r_zero)
        delta = 0.5 * np.power(bs - r_zero, 2) / var_detector
        # scipy's gammainc is already regularized (== Igor's gammp), so no extra division by gamma(1.5)
        inc_gamma = np.where(r_zero < bs,
                             gamma(1.5) * (1.0 - gammainc(1.5, delta)),
                             gamma(1.5) * (1.0 + gammainc(1.5, delta)))
        f_sub_s = 0.5 * (1.0 + erf((r_zero - bs) / np.sqrt(2.0 * var_detector)))  # JGB eq (11)
        f_sub_s = np.where(f_sub_s <= 0.0, small_number, f_sub_s)
        fr = 1.0 + np.sqrt(var_detector) * np.exp(-1.0 * delta) / (r_zero * f_sub_s * np.sqrt(2.0 * np.pi))  # eq (12)
        fv = inc_gamma / (f_sub_s * np.sqrt(np.pi)) - np.power(r_zero * (fr - 1.0), 2) / var_detector  # eq (13)
        rmd = fr * r_zero
        var_r1 = var_beam + var_detector * fv + var_gravity
        rm = rmd + 0.5 * var_r1 / rmd
        var_r = var_r1 - 0.5 * (var_r1 / rmd) * (var_r1 / rmd)
        var_r = np.where(var_r < 0, 0.0, var_r)
        self.q_average = (4.0 * np.pi / lambda_val) * np.sin(0.5 * np.arctan(rm / l2))
        self.sigma_q = self.q_average * np.sqrt(var_r / (rmd * rmd) + var_lambda)  # JGB eq (4)
        self.f_subs = f_sub_s + 1e-8  # Keep the values from being too small

    def calculate_distance_from_beam_center(self, pixel_value: float | np.ndarray, x_or_y: str) -> float | np.ndarray:
        if x_or_y.lower() == "x":
            pixel_center = self.x_center
        else:
            pixel_center = self.y_center
        return self.coeff * np.tan(pixel_value - pixel_center) * self.pixel_size / self.coeff

    # Calculate Q Range Slicer and its helper methods
    def calculate_q_range_slicer(self):
        # Detector values pixel size in mm
        self.generate_ones_data()
        self.generate_standard_mask()
        # Calculate Qx and Qy values
        # Per-pixel Q from the pixel's real-space position (Igor: V_CalcQval, V_CalcQX, V_CalcQY). [i][j] is (x_i, y_j)
        x_distances, y_distances = self.pixel_distances()
        x_2d, y_2d = np.meshgrid(x_distances, y_distances, indexing='ij')
        two_theta = np.arctan(np.hypot(x_2d, y_2d) / self.SDD)
        phi = np.arctan2(y_2d, x_2d)
        self.q_2d_values = (4 * np.pi / self.lambda_val) * np.sin(two_theta / 2)
        # Project onto the detector plane (the remainder is qz)
        self.qx_2d_values = self.q_2d_values * np.cos(two_theta / 2) * np.cos(phi)
        self.qy_2d_values = self.q_2d_values * np.cos(two_theta / 2) * np.sin(phi)
        # Axes for plotting the panel as an image: linear from the min to max Q, as Igor's SetScale/I does
        self.qx_values = np.linspace(self.qx_2d_values.min(), self.qx_2d_values.max(), self.x_pixels)
        self.qy_values = np.linspace(self.qy_2d_values.min(), self.qy_2d_values.max(), self.y_pixels)
        min_theta = np.arctan(self.beam_stop_size / (2 * self.detector_distance))
        min_q = (4 * np.pi / self.lambda_val) * np.sin(min_theta / 2)
        self.intensity_2D = np.where(abs(self.q_2d_values) > min_q, self.intensity_2D, 1e-10)
        self.calculate()

    def generate_ones_data(self):
        """Create an array of 1s as a basis for the 2D intensity values. These 1s willed be scaled relative to the
        average intensity for each pixel"""
        self.intensity_2D = np.ones((self.x_pixels, self.y_pixels))

    def generate_standard_mask(self):
        """ Generate an array that uses 1 to represent a masked pixel and 0 otherwise. The outer two pixels are masked
        by default."""
        self.mask = np.array([[1 if i <= 1 or i >= self.x_pixels - 2 or j <= 1 or j >= (self.y_pixels - 2) else 0
                      for i in range(self.x_pixels)] for j in range(self.y_pixels)]).transpose()

    def include_pixel(self, x_val: int | np.ndarray, y_val: int | np.ndarray, mask: np.ndarray) -> np.ndarray[bool]:
        return mask == 0

    # Slicer recturn method for all the values need to return to slicer
    def slicer_return(self) -> dict:
        slicer_return = {}
        slicer_return["averageType"] = self.average_type
        slicer_return["detectorSections"] = self.detector_sections
        slicer_return["phi"] = self.phi
        slicer_return["phiUpper"] = self.phi_upper
        slicer_return["phiLower"] = self.phi_lower
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
        """Vectorized sector selection (Igor: dphi_pixel). Accepts arrays of positions."""
        radius = np.hypot(x_val, y_val)
        with np.errstate(divide='ignore', invalid='ignore'):
            dot_product = np.where(radius > 0, (x_val * self.phi_x + y_val * self.phi_y) / radius, 1.0)
        dphi_pixel = np.arccos(np.clip(dot_product, -1.0, 1.0))
        forward = dphi_pixel < self.d_phi
        mirror = (np.pi - dphi_pixel) < self.d_phi
        if self.detector_sections == "right":
            selected = forward
        elif self.detector_sections == "left":
            selected = mirror
        else:
            selected = forward | mirror
        return selected & (mask == 0)


class Rectangular(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "rectangular"

    def include_pixel(self, x_val, y_val, mask):
        """Vectorized rectangular selection. Accepts arrays of positions."""
        corrected_radius = np.hypot(x_val, y_val)
        with np.errstate(divide='ignore', invalid='ignore'):
            dot_product = np.where(corrected_radius > 0,
                                   (x_val * self.phi_x + y_val * self.phi_y) / corrected_radius, 1.0)
        dphi_pixel = np.arccos(np.clip(dot_product, -1.0, 1.0))
        d_perpendicular = corrected_radius * np.sin(dphi_pixel)
        in_strip = d_perpendicular <= 0.5 * self.q_width * self.pixel_size
        if self.detector_sections == "left":
            side = dot_product >= 0
        elif self.detector_sections == "right":
            side = dot_product < 0
        else:
            side = np.ones_like(in_strip, dtype=bool)
        return in_strip & side & (mask == 0)

class Elliptical(Slicer):
    def __init__(self, params):
        super().__init__(params)
        self.average_type = "elliptical"

    def calculate_q(self, theta):
        return super().calculate_q(theta)

    def calculate_radius(self, x_val, y_val):
        # Supposed to be super().calculate _radius but DNE in slicer class
        i_circular = super().get_i_radius(x_val, y_val)
        rho = np.atan(x_val / y_val) - self.phi
        return np.floor(i_circular * np.sqrt(
            np.cos(rho) * np.cos(rho) + self.aspect_ratio * np.sin(rho) * np.sin(rho))) + 1


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
