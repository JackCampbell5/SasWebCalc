def create_js(name=None, default=None, type_val=None, unit=None, readonly=None, options=None,
              min_val=None, max_val=None, step=None, range_id=None, hidden=None, lower_limit=None,
              upper_limit=None):
    # Add to the correct category
    js_array = {}
    if min_val is not None and min_val != "":
        js_array["min"] = min_val
    if step is not None and step != "":
        js_array["step"] = step
    if max_val is not None and max_val != "":
        js_array["max"] = max_val
    if range_id is not None and range_id != "":
        js_array["range_id"] = range_id
    if hidden is not None and hidden != "":
        js_array["hidden"] = hidden
    if lower_limit is not None and lower_limit != "":
        js_array["lower_limit"] = lower_limit
    if upper_limit is not None and upper_limit != "":
        js_array["upper_limit"] = upper_limit
    if name is not None and name != "":
        js_array["name"] = name
    if default is not None and default != "":
        js_array["default"] = default
    if type_val is not None and type_val != "":
        js_array["type"] = type_val
    if unit is not None and unit != "":
        js_array["unit"] = unit
    else:
        js_array["unit"] = ''
    if readonly is not None and readonly != "":
        js_array["readonly"] = readonly
    if options is not None and options != "":
        js_array["options"] = options
    return js_array
    # Ones that are not none add to the array


def create_sample_table(name='Sample Table', default='Chamber', type_val='select', unit='', readonly=None,
                        options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for sample_table

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = ['Chamber', 'Huber']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_wavelength_input(name='Wavelength', default=6.0, type_val='number', unit='nm;', readonly=None,
                            options=None, step=None, hidden=None, range_id=None, lower_limit=4.8, upper_limit=20.0):
    """Takes in the appropriate parameters to set up the js dictionary for wavelength_input

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param str range_id: The id of the range of the parameter
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit,
                     hidden=hidden)


def create_wavelength_spread(name='Wavelength Spread', default=13.9, type_val='select', unit='', readonly=None,
                             options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for wavelength_spread

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [9.7, 13.9, 15, 22.1]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_beam_flux(name='Beam Flux', default='', type_val='number', unit='n cm<sup>-2</sup> s<sup>-1</sup>',
                     readonly=True, options=None, step=None, hidden=None, range_id=None, lower_limit=None,
                     upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_flux

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_figure_of_merit(name='Figure of Merit', default='', type_val='number', unit='', readonly=True,
                           options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_flux

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_attenuators(name='Attenuators', default='', type_val='number', unit=None, readonly=True,
                       options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for attenuators

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_attenuation_factor(name='Attenuation Factor', default='', type_val='number', unit=None, readonly=True,
                              options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for attenuation_factor

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_guide_config(name='Guides', default=0, type_val='select', unit=None, readonly=None,
                        options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for guide_config

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_source_aperture(name='Source Aperture', default=1.43, type_val='select', unit='cm', readonly=None,
                           options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for source_aperture

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [1.43, 2.54, 3.81, 5.08]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_sample_aperture(name='Sample Aperture', default=0.500, type_val='select', unit='inch', readonly=None,
                           options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for sample_aperture

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_custom_aperture(name='Aperture Diameter', default=13, type_val='number', unit='mm', readonly=None,
                           options=None, step=None, hidden=True, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for custom_aperture

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_ssd(name='Source-To-Sample Distance', default=1627, type_val='number', unit='cm', readonly=True,
               options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for ssd

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_sdd_input_box(name='Detector Distance', default=100, type_val='number', unit='cm', readonly=None,
                         options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for ssd_input_box

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_sdd_defaults(name=' ', default=100, type_val='range', unit='', readonly=None,
                        options=None, range_id='ng7SDDDefaultRange', hidden=None, lower_limit=90, upper_limit=1532):
    """Takes in the appropriate parameters to set up the js dictionary for ssd_defaults

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param str range_id: The id of the range of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit is the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [100, 400, 1300, 1530]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, range_id=range_id, hidden=hidden, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_offset_input_box(name='Detector Offset', default=0, type_val='number', unit='cm', readonly=None,
                            options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for offset_input_box

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_offset_defaults(name=' ', default=0, type_val='range', unit='', readonly=None,
                           options=None, range_id='ng7OffsetDefaultRange', hidden=None, lower_limit=0,
                           upper_limit=25):
    """Takes in the appropriate parameters to set up the js dictionary for offset_defaults

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param str range_id: The id of the range of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit is the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [0, 5, 10, 15, 20, 25]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, range_id=range_id, hidden=hidden, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_sdd(name='Sample-To-Detector Distance', default=100, type_val='number', unit='cm', readonly=True,
               options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for sdd

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_beam_diameter(name='Beam Diameter', default='', type_val='number', unit='cm', readonly=True,
                         options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_diameter

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_beam_stop_size(name='Beam Stop Diameter', default='', type_val='number', unit='cm', readonly=True,
                          options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_stop_size

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_min_q(name='Minimum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True,
                 options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for min_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_max_q(name='Maximum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True,
                 options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for max_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_max_vertical_q(name='Maximum Vertical Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                          readonly=True,
                          options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for min_vertical_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_maximum_horizontal_q(name='Maximum Horizontal Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                                readonly=True, options=None, step=None, hidden=None, range_id=None, lower_limit=None,
                                upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for maximum_horizontal_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param str range_id: The id of the range of the range
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit if the parameter is a range
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit,
                     upper_limit=upper_limit)


def create_number_input(name=None, default=0.0, type_val='number', unit='Å', readonly=None,
                        options=None, step=None, range_id=None, hidden=None, lower_limit=None,
                        upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary for a numerical input

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param float step: The amount the number in the input box will change by each arrow
    :param str range_id: The id of the range of the range
    :param float or str lower_limit: The lower limit if the parameter is a range
    :param float or str upper_limit: The upper limit if the parameter is a range
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, step=step, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit,
                     hidden=hidden)


def create_secondary_elements(more_data=None, ssd=True, offset=True):
    if more_data is not None:
        result = more_data
    else:
        result = {}
    if ssd:
        result["sDDInputBox"] = {"cat1": "Detector", "name1": "sDDDefaults", "cat2": "Detector", "name2": "sDDInputBox"}
        result["sDDDefaults"] = {"cat1": "Detector", "name1": "sDDInputBox", "cat2": "Detector", "name2": "sDDDefaults"}
    if offset:
        result["offsetInputBox"] = {"cat1": "Detector", "name1": "offsetDefaults", "cat2": "Detector",
                                    "name2": "offsetInputBox"}
        result["offsetDefaults"] = {"cat1": "Detector", "name1": "offsetInputBox", "cat2": "Detector",
                                    "name2": "offsetDefaults"}
    return result


def check_params(params={}):
    return_array = params.copy()
    for name in params.keys():
        if len(params[name]) < 2 and name != "hidden":
            return_array.pop(name)
    return return_array


def generate_js_array(name=True):
    output = {}
    output["Sample"] = {"name": "Sample Area Settings"} if name else {}
    output["Wavelength"] = {"name": "Wavelength Settings"} if name else {}
    output["Collimation"] = {"name": "Collimation Settings"} if name else {}
    output["Detector"] = {"name": "Detector Settings"} if name else {}
    output["QRange"] = {"name": "Calculated Q Range"} if name else {}
    output["hidden"] = {"secondary_elements": {}}
    return output
