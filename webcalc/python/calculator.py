from typing import Optional, Union, List, Dict

from sasmodels.kernel import KernelModel
from sasmodels.direct_model import call_kernel

from .instrument import Instrument, Data
from .slicers import Slicer


class Calculator:
    """
    The primary calculation class. This will accept instances necessary to perform the entire calculation.
    """

    def __init__(self, instrument: Instrument, model: KernelModel, averaging: Slicer, sample: Optional = None):
        # The instrument simulator class that this calculation will use
        self.instrument = instrument
        # The model describing the sample for this calculation. e.g. A spherical model for SANS.
        self.model = model
        # The averaging method use for this calculation. e.g. Circular average for a 2D SANS pattern
        self.averaging = averaging
        # Placeholder for future addition of the Sample class that will hold sample specific information.
        self.sample = None
        # The class to hold all calculated data
        self.data = Data(self.instrument, {})

    def calculate(self, model_params: Dict[str, Union[int, float]]):
        """
        The primary calculation routine.
        :param model_params: The model calculator uses the params at the time of the call, not instantiation.
        """
        # Calculate the as-viewed scattering pattern from the instrument without applying any model calculation
        #   This should calculate the resolution per point, and uncertainty in intensity.
        self.instrument.sas_calc()
        # Apply any sample-specific modifications to the base pattern
        if self.sample:
            # TODO: we need a Sample class...
            pass
        # Calculate the as-viewed scattering pattern using the model, assuming the resolution and information from
        #   the instrument class
        kernel = self.model.make_kernel(self.instrument.data.q_values)
        self.data.intensity = call_kernel(kernel, model_params)
        # Calculate the averaged representation of the data
        self.averaging.calculate()

    def format_data_for_return(self) -> Dict[str, Union[str, int, float, List]]:
        """Formats the Data() object into a JSON-like dictionary that matches what the front-end expects.
        :return: A JSON-formatted set of all calculated data."""
        return_dict = {}  # TODO: Populate this dictionary
