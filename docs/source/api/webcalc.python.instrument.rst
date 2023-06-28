webcalc\.python\.instrument package
===================================
This is the overall organization of the variables in the instrument class

.. code:: python

    #Args:
        #instrument: String defining instrument name
        #params: Dictionary containing the following information:
            #{
                #"param_name_001" :
                    #{
                        #name: str,  # Display name for parameter
                        #default: Union[float, int, str],  # Current value
                        #type: Optional[str],  # input type, either ["string", "number", or "option"]
                        #min: Optional[Union[float, int, str]],
                        #max: Optional[Union[float, int, str]],
                        #options: Optional[List],
                        #unit: Optional[str],
                    #},
                #...
            #}

        #Returns: The following dictionary {
            #Qx: [],
            #dQx: [],
            #Qy: [],
            #dQy: [],
            #Iqxy: [],
            #q: [],
            #dq: [],
            #Iq: [],
            #beamflux: float,
        #}

.. toctree::

    webcalc.python.instrument.aperture
    webcalc.python.instrument.beamstop
    webcalc.python.instrument.collimation
    webcalc.python.instrument.detector
    webcalc.python.instrument.guide
    webcalc.python.instrument.wavelength
    webcalc.python.instrument.data
    webcalc.python.instrument.instrument
    webcalc.python.instrument.NoInstrument
    webcalc.python.instrument.ng7sans
    webcalc.python.instrument.ngb30sans
    webcalc.python.instrument.ngb10sans



.. automodule:: webcalc.python.instrument
    :members: calculate_instrument,set_params
    :show-inheritance:
    :undoc-members:

