import math
import numpy as np

from .units import Converter
# TODO: Replace all math.unit instances with nxsunit values
# TODO: Replace all nodes with Instrument parameters
# TODO: Call slicer directly using known parameters


def calculate_instrument(instrument, params):
    # type: (str, dict) -> dict
    """ The base calculation script. Creates an instrument class, calculates the instrumental resolution for the
    configuration, and returns two list of intensities
    Args:
        instrument: String defining instrument name
        params: Dictionary containing the following information:
            {
                instrument: "Name",
                wavelength:
                {
                    lambda: <value>,
                    lambda_unit: <unit>,
                    d_lambda: <value>,
                    d_lambda_unit: <unit>,
                    attenuation_factor: <value>
                },
                collimation:
                {
                    source_aperture: <value>,  # Source aperture radius
                    source_aperture_unit: "unit",  # Unit string for source aperture radius (e.g. mm, cm, centimeters)
                    ssd: <value>,  # Source to sample distance
                    ssd_unit: "unit",
                    ssad: <value>, # Source to sample aperture distance
                    ssad_unit: "unit",
                    sample_aperture: <value>,
                    sample_aperture_units: "unit",
                },
                detectors:
                [
                    {
                        sdd: <value>,
                        sdd_units: "unit",
                        sadd: <value>,
                        sadd_units: "unit",
                        offset: <value>,
                        offset_unit: "unit",
                        pixel_size_x: <value>,
                        pixel_size_x_unit: "unit"
                        pixel_size_y: <value>,
                        pixel_size_y_unit: "unit"
                        pixel_size_z: <value>,
                        pixel_size_z_unit: "unit"
                        pixels_x: <value>,
                        pixels_y: <value>,
                        pixels_z: <value>,
                        dead_time: <value>
                    },
                    ...,
                    {}
                ],
                constants:
                {

                }
            }

    Returns: [[1D resolutions], [2D resolutions]
    """
    # TODO: Create classes for all instruments
    i_class = NG7SANS(instrument, params) if instrument == 'ng7' else Instrument(instrument, params)
    return i_class.sas_calc()


class Detector:
    def __init__(self, params):
        self.sadd = 0.0
        self.sadd_unit = 'cm'
        self.sdd = 0.0
        self.sdd_unit = 'cm'
        self.offset = 0.0
        self.offset_unit = 'cm'
        self.pixel_size_x = 0.0
        self.pixel_size_x_unit = 'cm'
        self.pixel_size_y = 0.0
        self.pixel_size_y_unit = 'cm'
        self.pixel_size_z = 0.0
        self.pixel_size_z_unit = 'cm'
        self.pixel_no_x = 0
        self.pixel_no_y = 0
        self.pixel_no_z = 0
        self.dead_time = 0
        self.beam_center_x = 0.0
        self.beam_center_y = 0.0
        self.beam_center_z = 0.0
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.set_params(params)

    def set_params(self, params=None):
        if not isinstance(params, dict):
            return
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.calculate_all_beam_centers()

    def calculate_all_beam_centers(self):
        self.calculate_beam_center_x()
        self.calculate_beam_center_y()
        self.calculate_beam_center_z()

    def calculate_beam_center_x(self):
        # Find the number of x pixels in the detector
        x_pixels = self.pixel_no_x
        # Get pixel size in mm and convert to cm
        dr = self.get_pixel_size_x()
        # Get detector offset in cm
        offset = self.get_offset()
        self.beam_center_x = offset / dr + x_pixels / 2 + 0.5

    def calculate_beam_center_y(self):
        # Find the number of x pixels in the detector
        y_pixels = self.pixel_no_y
        # Get detector offset in cm
        self.beam_center_y = y_pixels / 2 + 0.5

    def calculate_beam_center_z(self):
        # Find the number of x pixels in the detector
        z_pixels = self.pixel_no_z
        # Get detector offset in cm
        self.beam_center_z = z_pixels / 2 + 0.5

    def get_pixel_size_x(self):
        return self.d_converter(self.pixel_size_x, self.pixel_size_x_unit)

    def get_pixel_size_y(self):
        return self.d_converter(self.pixel_size_y, self.pixel_size_y_unit)

    def get_pixel_size_z(self):
        return self.d_converter(self.pixel_size_z, self.pixel_size_z_unit)

    def get_ssd(self):
        return self.d_converter(self.sdd, self.sdd_unit)

    def get_sadd(self):
        return self.d_converter(self.sadd, self.sadd_unit)

    def get_offset(self):
        return self.d_converter(self.offset, self.offset_unit)



class Instrument:
    isReal = False

    def __init__(self, name="", params=None):
        if not params:
            params = None
        # Only store values used for calculations in Instrument class
        self.beam_stop = {

        }
        self.calculated_values = {

        }
        self.name = name
        # TODO: Create Collimation, Aperture, and Wavelength Classes
        # Wavelength dictionary values
        self.wavelength = 0.0
        self.wavelength_unit = 'cm'
        self.wavelength_spread = 0.0
        self.wavelength_spread_unit = '%'
        self.attenuation_factor = 0.0
        self.wavelength = {}
        # Collimation dictionary values
        self.source_aperture = 0.0
        self.source_aperture_unit = 'cm'
        self.sample_aperture = 0.0
        self.sample_aperture_unit = 'cm'
        self.ssd = 0.0
        self.ssd_unit = 'cm'
        self.ssad = 0.0
        self.ssad_unit = 'cm'
        self.collimation = {}
        # Detector values
        self.detectors = []
        self.flux = 0.0
        self.bs_factor = 0.0
        self.d_converter = Converter('cm')
        self.t_converter = Converter('s')
        self.load_params(params)

    """
        Pseudo-abstract method to initialize constants associated with an instrument
    """
    def load_params(self, params):
        raise NotImplementedError('The abstract load_params() method must be implemented by Instrument sub-classes.')

    def sas_calc(self):
        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculate_instrument_parameters()
        return self.calculated_values

    def calculate_instrument_parameters(self):
        # Calculate the beam stop diameter
        self.calculate_beam_stop_diameter()
        # Calculate the estimated beam flux
        self.calculate_beam_flux()
        # Calculate the figure of merit
        self.calculate_figure_of_merit()
        # Calculate the number of attenuators
        self.calculate_attenuators()
        # Do Circular Average of an array of 1s
        for index in self.detectors:
            self.calculate_min_and_max_q(index)
            # TODO: This might not be needed here...
            self.calculate_q_range_slicer(index)

    def calculate_attenuation_factor(self, index=0):
        a2 = self.get_sample_aperture_size()
        beam_diam = self.get_beam_diameter(index)
        a_pixel = self.detectors[index].pixels.xSize
        i_pixel_max = self.detectors[index].perPixelMaxFlux

        num_pixels = (math.pi/4) * (0.5 * (a2 + beam_diam)/a_pixel)**2
        i_pixel = self.get_beam_flux()/num_pixels
        atten = 1.0 if i_pixel < i_pixel_max else i_pixel_max/i_pixel
        self.wavelength.attenuation_factor = atten if atten == 1.0 else atten.toNumeric()

    def calculate_attenuators(self):
        self.calculate_attenuation_factor()
        atten = self.get_attenuation_factor()
        af = 0.498 + 0.0792 * self.get_wavelength() - 1.66e-3 * self.get_wavelength()**2
        nf = -1*math.log(atten)/af
        num_atten = math.ceil(nf)
        if num_atten > 6:
            num_atten = 7 + math.floor((num_atten - 6) / 2)
        self.wavelength.number_of_attenuators = num_atten

    def calculate_beam_center_x(self, index=0):
        # Find the number of x pixels in the detector
        x_pixels = self.detectors[index].pixels.dimensions[0]
        # Get pixel size in mm and convert to cm
        dr = self.detectors[index].pixels.xSize
        # Get detector offset in cm
        offset = self.get_detector_offset()
        self.detectors[index].beam_center_x = offset/dr + x_pixels/2 + 0.5

    def calculate_beam_diameter(self, index=0, direction='maximum'):
        # Update all instrument calculations needed for beam diameter
        self.calculate_source_to_sample_aperture_distance()
        self.calculate_sample_to_detector_distance(index)
        # Get instrumental values
        source_aperture = self.get_source_aperture_size()
        sample_aperture = self.get_sample_aperture_size()
        ssd = self.get_source_to_sample_aperture_distance()
        sdd = self.get_sample_aperture_to_detector_distance(index)
        wavelength = self.get_wavelength()
        wavelength_spread = self.get_wavelength_spread()
        if self.collimation.get('lens') is True:
            # If LENS configuration, the beam size is the source aperture size
            # FIXME: This is showing -58 cm... Why?!?!
            self.beam_stops[index].value = self.get_source_aperture_size()
        # Calculate beam width on the detector
        beam_width = source_aperture * sdd/ssd + sample_aperture * (ssd + sdd) / ssd
        # Beam height due to gravity
        bv3 = ((ssd + sdd) * sdd) * wavelength**2
        bv4 = bv3 * wavelength_spread
        bv = beam_width + 0.0000125 * bv4
        # Larger of the width*safetyFactor and height
        bm_bs = self.bs_factor * beam_width
        bm = bm_bs if bm_bs > bv else bv
        if direction == 'vertical':
            beam_diam = bv
        elif direction == 'horizontal':
            beam_diam = bm_bs
        else:
            beam_diam = bm
        self.beam_stops[index].value = beam_diam

    def calculate_beam_stop_diameter(self, index=0):
        self.calculate_beam_diameter(index, 'maximum')
        beam_diam = self.get_beam_diameter(index)
        for i in self.beam_stops.keys():
            beam_stop_dict = self.beam_stops[i]
            if beam_stop_dict.size >= beam_diam:
                self.beam_stops[index].value = beam_stop_dict.size
                return
        else:
            # If this is reached, that means the beam diameter is larger than the largest known beam stop
            self.beam_stops[index].value = self.beam_stops[len(self.beam_stops) - 1].size

    def calculate_beam_stop_projection(self, index=0):
        self.get_sample_to_detector_distance(index)
        self.calculate_beam_diameter(index)
        self.calculate_beam_stop_diameter(index)
        bs_diam = self.get_beam_stop_diameter(index)
        sample_aperture = self.get_sample_aperture_size()
        l2 = self.get_sample_aperture_to_detector_distance()
        l_beam_stop = 20.1 + 1.61 * self.get_beam_stop_diameter()  # distance in cm from beam stop to anode plane
        return bs_diam + (bs_diam + sample_aperture) * l_beam_stop/(l2 - l_beam_stop)  # Return in cm

    def calculate_beam_flux(self):
        # FIXME: Flux calculation is about 7x too high
        # Get constants
        # TODO: Get values from correct locations
        peak_lambda = self.flux.peakWavelength
        peak_flux = self.flux.peakFlux
        guide_gap = self.collimationOptions.gapAtStart
        guide_loss = self.collimationOptions.transmissionPerUnit
        guide_width = self.collimationOptions.width
        trans1 = self.flux.trans1
        trans2 = self.flux.trans2
        trans3 = self.flux.trans3
        b = self.flux.b
        c = self.flux.c
        source_aperture = self.get_source_aperture_size()
        sample_aperture = self.get_sample_aperture_size()
        sdd = self.get_sample_to_detector_distance()
        wave = self.get_wavelength()
        lambda_spread = self.get_wavelength_spread()
        guides = self.get_number_of_guides()

        # Run calculations
        alpha = (source_aperture + sample_aperture) / (2 * sdd)
        f = (guide_gap * alpha) / (2 * guide_width)
        trans4 = (1 - f) * (1, f)
        trans5 = math.exp(guides * math.log(guide_loss))
        trans6 = 1 - wave * (b - (guides / 8) * (b - c))
        total_trans = trans1, trans2, trans3 * trans4 * trans5 * trans6

        area = math.pi * sample_aperture * sample_aperture / 4
        d2_phi = peak_flux / (2 * math.pi)
        d2_phi = d2_phi * math.exp(4 * math.log(peak_lambda / wave))
        d2_phi = d2_phi * math.exp(-1 * math.pow(peak_lambda / wave, 2))
        solid_angle = (math.pi / 4) * (sample_aperture / sdd) * (sample_aperture / sdd)
        beam_flux = area * d2_phi * lambda_spread * solid_angle * total_trans
        # TODO: Store beam_flux in appropriate location

    def calculate_distance_from_beam_center(self, n_pixels, pixel_center, pixel_size, coeff):
        pixel_array = np.array(n_pixels.keys())
        raw_value = (pixel_array - pixel_center) * pixel_size
        return coeff * math.tan((raw_value / coeff))

    def calculate_figure_of_merit(self):
        figure_of_merit = math.pow(self.get_wavelength(), 2) * self.get_beam_flux()
        return figure_of_merit.toNumeric()

    def calculate_min_and_max_q(self, index=0):
        sdd = self.get_sample_to_detector_distance()
        offset = self.get_detector_offset()
        wave = self.get_wavelength()
        # TODO: Get actual values from classes, as needed
        pixel_size = self.detectorOptions[index].pixels.xSize
        det_width = pixel_size * self.detectorOptions[index].pixels.dimensions[0]
        bs_projection = self.calculate_beam_stop_projection()
        # Calculate Q-maximum and populate the page
        radial = math.sqrt(math.pow(0.5 * det_width, 2) + math.pow((0.5 * det_width) + offset, 2))
        # TODO: Store q_max and q_min in appropriate places
        q_max = 4 * (math.pi / wave) * math.sin(0.5 * math.atan(radial / sdd))
        # Calculate Q-minimum and populate the page
        q_min = (math.pi / wave) * (bs_projection + pixel_size + pixel_size) / sdd
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) + offset) / sdd)
        q_max_horizon = 4 * (math.pi / wave) * math.sin(0.5 * theta)
        # Calculate Q-maximum and populate the page
        theta = math.atan(((det_width / 2.0) / sdd))
        q_max_vert = 4 * (math.pi / wave) * math.sin(0.5 * theta)
        # TODO: Store q_max_vert and q_max_horizon in appropriate places

    def calculate_source_to_sample_aperture_distance(self):
        self.ssdNode.value = (self.collimationOptions.lengthMaximum
                              - self.collimationOptions.lengthPerUnit * self.get_number_of_guides()
                              - self.sampleTableOptions[self.sampleTableNode.value].offset
                              - self.sampleTableOptions[self.sampleTableNode.value].apertureOffset)

    # TODO: Keep in the javascript?
    def calculate_wavelength_range(self):
        current_spread = self.wavelengthSpreadNode.value
        constants = self.wavelengthOptions.spreads[current_spread].constants
        calculated_minimum = constants[0] + (constants[1] / self.wavelengthOptions.max_rpm)
        minimum = calculated_minimum if calculated_minimum > self.wavelengthOptions.minimum else self.wavelengthOptions.minimum
        self.wavelengthOptions.spreads[current_spread].range = [minimum, self.wavelengthOptions.maximum]
        if self.get_wavelength() < minimum:
            self.wavelengthNode.value = minimum.toNumeric()

    # Various class updaters
    def update_wavelength(self, run_sas_calc=True):
        self.calculate_wavelength_range()
        if run_sas_calc:
            self.sas_calc()

    # TODO: This might be able to stay in the javascript
    def update_guides(self, run_sas_calc=True):
        # Get guide nodes for the specific instrument
        all_aperture_options = self.sourceApertureNode.options
        guide_aperture_options = self.collimationOptions.options[self.guideConfigNode.value].apertureOptions
        # Show only source apertures allowed for the current guide configuration
        for aperture in all_aperture_options:
            aperture_value = all_aperture_options[aperture].value
            if math.compare(aperture_value, guide_aperture_options).includes(0):
                all_aperture_options[aperture].disabled = False
                all_aperture_options[aperture].hidden = False
                all_aperture_options[aperture].selected = True
            else:
                all_aperture_options[aperture].disabled = True
                all_aperture_options[aperture].hidden = True
        if run_sas_calc:
            self.sas_calc()

    # Various class getter functions
    # Use these to be sure units are correct
    def get_attenuation_factor(self):
        # The attenuation factor value calculated based on the number of attenuators
        return self.attenuationFactorNode.value

    def get_attenuators(self):
        # Number of attenuators in the beam
        return self.attenuatorNode.value

    def get_beam_flux(self):
        # Beam flux in cm^-2-s^-1
        return self.beamfluxNode.value

    def get_beam_diameter(self, index=0):
        # Beam diameter in centimeters
        return self.beamSizeNodes[index].value

    def get_beam_stop_diameter(self, index=0):
        # Beam stop diameter in inches
        # TODO: Convert to centimeters
        return self.beamStopSizeNodes[index].value

    def get_number_of_guides(self):
        # Number of neutron guides in the beam
        guides = self.guideConfigNode.value
        if guides == "LENS":
            guides = 0
        else:
            guides = int(guides)
        return guides

    def get_sample_aperture_size(self):
        # Sample Aperture radius in centimeters
        return self.sampleApertureNode.value

    def get_source_aperture_size(self):
        # Source Aperture radius in centimeters
        return self.sourceApertureNode.value

    def get_sample_aperture_to_detector_distance(self, index=0):
        # SADD in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_sadd()

    def get_sample_to_detector_distance(self, index=0):
        # SDD in centimeters
        table_offset = self.sampleTableOptions[self.sampleTableNode.value].offset
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        sdd = detector.get_ssd()
        return sdd + table_offset

    def get_detector_offset(self, index=0):
        # Detector offset in centimeters
        try:
            detector = self.detectors[index]
        except IndexError:
            return 0.0
        return detector.get_offset()

    def get_source_to_sample_distance(self):
        # SSD in centimeters
        return self.ssdNode.value

    def get_source_to_sample_aperture_distance(self):
        # SSAD in centimeters
        aperture_offset = self.sampleTableOptions[self.sampleTableNode.value].apertureOffset
        return self.ssdNode.value - aperture_offset

    def get_wavelength(self):
        # Wavelength in Angstroms
        return self.wavelengthNode.value

    def get_wavelength_spread(self):
        # Wavelength spread in percent
        return self.wavelengthSpreadNode.value


class NG7SANS(Instrument):
    def __init__(self, name, params):
        super().__init__(name, params)

    def load_params(self, params):
        # TODO: Take params and load them in
        pass
