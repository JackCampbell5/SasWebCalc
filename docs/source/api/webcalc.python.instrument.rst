webcalc\.python\.instrument package
===================================
This is the overall organization of the variables in the instrument class


.. toctree::

    webcalc.python.instrument.aperture
    webcalc.python.instrument.beamstop
    webcalc.python.instrument.collimation
    webcalc.python.instrument.detector
    webcalc.python.instrument.guide
    webcalc.python.instrument.wavelength
    webcalc.python.instrument.data
    webcalc.python.instrument.instrument
    webcalc.python.instrument.ng7sans
    webcalc.python.instrument.ngb30sans
    webcalc.python.instrument.ngb10sans


.. code:: python

    #Args:
    #    instrument: String defining instrument name
    #    params: Dictionary containing the following information:
    #        {
    #            instrument: "Name",
    #            wavelength:
    #            {
    #                lambda: <value>,
    #                lambda_unit: <unit>,
    #                d_lambda: <value>,
    #                d_lambda_unit: <unit>,
    #                attenuation_factor: <value>
    #            },
    #            collimation:
    #            {
    #                source_aperture: <value>,  # Source aperture radius
    #                source_aperture_unit: "unit",  # Unit string for source aperture radius (e.g. mm, cm, centimeters)
    #                ssd: <value>,  # Source to sample distance
    #                ssd_unit: "unit",
    #                ssad: <value>, # Source to sample aperture distance
    #                ssad_unit: "unit",
    #                sample_aperture: <value>,
    #                sample_aperture_units: "unit",
    #            },
    #            detectors:
    #            [
    #                {
    #                    sdd: <value>,
    #                    sdd_units: "unit",
    #                    sadd: <value>,
    #                    sadd_units: "unit",
    #                    offset: <value>,
    #                    offset_unit: "unit",
    #                    pixel_size_x: <value>,
    #                    pixel_size_x_unit: "unit"
    #                    pixel_size_y: <value>,
    #                    pixel_size_y_unit: "unit"
    #                    pixel_size_z: <value>,
    #                    pixel_size_z_unit: "unit"
    #                    pixels_x: <value>,
    #                    pixels_y: <value>,
    #                    pixels_z: <value>,
    #                    dead_time: <value>
    #                },
    #                ...,
    #                {}
    #            ],
    #            constants:
    #            {
    #
    #            }
    #        }

.. automodule:: webcalc.python.instrument
    :members: calculate_instrument,set_params
    :show-inheritance:
    :undoc-members:

