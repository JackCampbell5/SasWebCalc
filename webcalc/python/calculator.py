from typing import Optional, Union, List, Dict

from sasdata.dataloader.data_info import Data2D
from sasmodels.kernel import KernelModel
from sasmodels.direct_model import call_kernel

from .instrument import Instrument
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
        # Data object to hold 2D data
        self.data = Data2D()

    def calculate(self, model_params: Dict[str, Union[int, float]]):
        """
        The primary calculation routine.
        :param model_params: The model calculator uses the params at the time of the call, not instantiation.
        """
        # Calculate the as-viewed scattering pattern from the instrument without applying any model calculation
        #   This should calculate the resolution per point, and uncertainty in intensity.
        self.instrument.sas_calc()
        # TODO: Create a sasdata.data_info Data2D object and pass that to the model and the slicer
        self.data.q_data = self.instrument.data.q_values
        # FIXME: This line is wrong - needs dqx data (and qx, qy, etc. data as well)
        self.data.dqx_data = self.instrument.data
        # Apply any sample-specific modifications to the base pattern
        if self.sample:
            # TODO: we need a Sample class...
            pass
        # Calculate the as-viewed scattering pattern using the model, assuming the resolution and information from
        #   the instrument class
        kernel = self.model.make_kernel(self.instrument.data.q_values)
        self.data.data = call_kernel(kernel, model_params)
        # TODO: From here, ensure the data in averaging is up-to-date
        # Calculate the averaged representation of the data
        self.averaging.calculate()

    def format_data_for_return(self) -> Dict[str, Union[str, int, float, List]]:
        """Formats the Data() object into a JSON-like dictionary that matches what the front-end expects.
        :return: A JSON-formatted set of all calculated data."""
        return_dict = {}  # TODO: Populate this dictionary
