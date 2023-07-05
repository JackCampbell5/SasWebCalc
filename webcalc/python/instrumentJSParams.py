def create_js(name=None, default=None, type_val=None, unit=None, readonly=None, options=None,
              min_val=None, max_val=None, range_id=None, hidden=None, lower_limit=None, upper_limit=None):
    # Add to the correct category
    js_array = {}
    if min_val is not None and min_val != "":
        js_array["min"] = min_val
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
    :param array options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = ['Chamber', 'Huber']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_wavelength_input(name='Wavelength', default=6.0, type_val='number', unit='nm;', readonly=None,
                            options=None, min_val=4.8, max_val=20.0, range_id=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for wavelength_input

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param str range_id: The id of the range of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, range_id=range_id, hidden=hidden)


def create_wavelength_spread(name='Wavelength Spread', default=13.9, type_val='select', unit='', readonly=None,
                             options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for wavelength_spread

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [9.7, 13.9, 15, 22.1]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_beam_flux(name='Beam Flux', default='', type_val='number', unit='n cm<sup>-2</sup> s<sup>-1</sup>',
                     readonly=True, options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_flux

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_figure_of_merit(name='Figure of Merit', default='', type_val='number', unit='', readonly=True,
                           options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_flux

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_attenuators(name='Attenuators', default='', type_val='number', unit=None, readonly=True,
                       options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for attenuators

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_attenuation_factor(name='Attenuation Factor', default='', type_val='number', unit=None, readonly=True,
                              options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for attenuation_factor

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_guide_config(name='Guides', default=0, type_val='select', unit=None, readonly=None,
                        options=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for guide_config

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
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
    :param array options: The options for the parameter if it needs specific options
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
    :param array options: The options for the parameter if it needs specific options
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    if options is None: options = [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, hidden=hidden)


def create_custom_aperture(name='Aperture Diameter', default=13, type_val='number', unit='mm', readonly=None,
                           options=None, min_val=None, max_val=None, hidden=True):
    """Takes in the appropriate parameters to set up the js dictionary for custom_aperture

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_ssd(name='Source-To-Sample Distance', default=1627, type_val='number', unit='cm', readonly=True,
               options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for ssd

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_ssd_input_box(name='Detector Distance', default=100, type_val='number', unit='cm', readonly=None,
                         options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for ssd_input_box

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_ssd_defaults(name='', default=100, type_val='range', unit='', readonly=None,
                        options=None, range_id='ng7SDDDefaultRange', hidden=None, lower_limit=90, upper_limit=1532):
    """Takes in the appropriate parameters to set up the js dictionary for ssd_defaults

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
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
                            options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for offset_input_box

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_offset_defaults(name='Detector Offset Defaults', default=0, type_val='range', unit='', readonly=None,
                           options=None, range_id='ng7OffsetDefaultRange', hidden=None, lower_limit=0,
                           upper_limit=25):
    """Takes in the appropriate parameters to set up the js dictionary for offset_defaults

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
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
               options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for sdd

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_beam_diameter(name='Beam Diameter', default='', type_val='number', unit='cm', readonly=True,
                         options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_diameter

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_beam_stop_size(name='Beam Stop Diameter', default='', type_val='number', unit='cm', readonly=True,
                          options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for beam_stop_size

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_min_q(name='Minimum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True,
                 options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for min_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_max_q(name='Maximum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True,
                 options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for max_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_max_vertical_q(name='Maximum Vertical Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                          readonly=True,
                          options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for min_vertical_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_maximum_horizontal_q(name='Maximum Horizontal Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                                readonly=True, options=None, min_val=None, max_val=None, hidden=None):
    """Takes in the appropriate parameters to set up the js dictionary for maximum_horizontal_q

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param array options: The options for the parameter if it needs specific options
    :param float min_val: The minimum value of the parameter
    :param float max_val: The maximum value of the parameter
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :returns: The JS dictionary of params encoded by create js
    :rtype: Dict
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly,
                     options=options, min_val=min_val, max_val=max_val, hidden=hidden)


def create_secondary_elements(more_data=None):
    if more_data is not None:
        result = more_data
    else:
        result = {}
    result["sDDInputBox"] = {"cat1": "Detector", "name1": "sDDDefaults", "cat2": "Detector", "name2": "sDDInputBox"}
    result["sDDDefaults"] = {"cat1": "Detector", "name1": "sDDInputBox", "cat2": "Detector", "name2": "sDDDefaults"}
    result["offsetInputBox"] = {"cat1": "Detector", "name1": "offsetDefaults", "cat2": "Detector",
                                "name2": "offsetInputBox"}
    result["offsetDefaults"] = {"cat1": "Detector", "name1": "offsetInputBox", "cat2": "Detector",
                                "name2": "offsetDefaults"}
    return result


def generate_js_array(name=True):
    output = {}
    output["Sample"] = {"name": "Sample Area Settings"} if name else {}
    output["Wavelength"] = {"name": "Wavelength Settings"} if name else {}
    output["Collimation"] = {"name": "Collimation Settings"} if name else {}
    output["Detector"] = {"name": "Detector Settings"} if name else {}
    output["QRange"] = {"name": "Calculated Q Range"} if name else {}
    output["hidden"] = {"secondary_elements": {}}
    return output


def create_python_helper(params=""):
    array_break = True
    master_array = []
    while array_break:
        value = params.find("///")
        if value == -1:
            array_break = False
        master_array.append(params[:value])
        params = params[value + 3:]
    output = []
    num = 0
    for value in master_array:
        if '{' in value:
            if num < len(output):
                if output[num][len(output[num]) - 1:] == ',':
                    output[num] = output[num][:len(output[num]) - 1]
                output[num] = output[num] + ")"
                num = num + 1
            output.append("output_params[\"" + value[:value.find("'")] + "\"] = create_js_params(")
            continue
        if ':' in value:
            if output[num][len(output[num]) - 1:] != ',' and output[num][len(output[num]) - 1:] != '(':
                output[num] = output[num] + "]"
            output[num] = output[num] + " " + value[:value.find(':')] + "=" + value[value.find(':') + 1:]
            continue
        if '\'' in value:
            output[num] = output[num] + "\'" + value
            continue
    if output[num][len(output[num]) - 1:] == ',':
        output[num] = output[num][:len(output[num]) - 1]
    output[num] = output[num] + ")"
    for place in range(len(output)):
        value = output[place]
        if "category" in value:
            val_num = value.find("category")
            value = value[:value.find('[')] + "[\"" + value[val_num + 11:value.find(",", val_num) - 1] + "\"]" + \
                    value[value.find('['):val_num - 2] + value[value.find("'", value.find("'", val_num) + 1) + 1:]
        output[place] = value

    # Next section
    return output


if __name__ == '__main__':
    var = "instrument_params_local: {///ng7BeamStopSizes': {///options: [2.54, 5.08, 7.62, 10.16]///},///ng7SampleTable': {///name: 'Sample Table',///default: \"Chamber\",///type: \"select\",///options: [///Chamber',///Huber'///],///unit: '',///category: 'ng7Sample',///},///ng7WavelengthInput': {///name: 'Wavelength',///default: 6.0,///min: 4.8,///max: 20.0,///type: \"number\",///unit: 'nm;',///category: 'ng7Wavelength',///},///ng7WavelengthSpread': {///name: 'Wavelength Spread',///default: 13.9,///type: \"select\",///category: 'ng7Wavelength',///unit: '',///options: [9.7, 13.9, 15, 22.1],///},///ng7BeamFlux': {///name: 'Beam Flux',///default: '',///type: \"number\",///unit: 'n cm<sup>-2</sup> s<sup>-1</sup>',///category: 'ng7Wavelength',///readonly: true,///},///ng7FigureOfMerit': {///name: 'Figure of merit',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7Attenuators': {///name: 'Attenuators',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7AttenuationFactor': {///name: 'Attenuation Factor',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7GuideConfig': {///name: 'Guides',///default: 0,///type: \"select\",///category: 'ng7Collimation',///unit: '',///options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS'],///},///ng7SourceAperture': {///name: 'Source Aperture',///default: 1.43,///type: \"select\",///unit: 'cm',///category: 'ng7Collimation',///options: [1.43, 2.54, 3.81, 5.08],///},///ng7SampleAperture': {///name: 'Sample Aperture',///default: 0.500,///type: \"select\",///unit: 'inch',///category: 'ng7Collimation',///options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom'],///},///ng7CustomAperture': {///name: 'Aperture Diameter',///default: 13,///type: \"number\",///unit: 'mm',///category: 'ng7Collimation',///hidden: true,///},///ng7SSD': {///name: 'Source-To-Sample Distance',///default: 1627,///type: \"number\",///unit: 'cm',///category: 'ng7Collimation',///readonly: true,///},///ng7SDDInputBox': {///name: 'Detector Distance',///default: 100,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///},///ng7SDDDefaults': {///name: '',///default: 100,///type: \"range\",///category: 'ng7Detector',///range_id: 'ng7SDDDefaultRange',///unit: '',///lower_limit: 90,///upper_limit: 1532,///options: [100, 400, 1300, 1530],///},///ng7OffsetInputBox': {///name: 'Detector Offset',///default: 0,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///},///ng7OffsetDefaults': {///name: '',///default: 0,///type: \"range\",///category: 'ng7Detector',///range_id: 'ng7OffsetDefaultRange',///unit: '',///lower_limit: 0,///upper_limit: 25,///options: [0, 5, 10, 15, 20, 25],///},///ng7SDD': {///name: 'Sample-To-Detector Distance',///default: 100,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///readonly: true,///},///ng7BeamDiameter': {///name: 'Beam Diameter',///default: '',///type: \"number\",///unit: \"cm\",///category: 'ng7Detector',///readonly: true,///},///ng7BeamStopSize': {///name: 'Beam Stop Diameter',///default: '',///type: \"number\",///unit: \"cm\",///category: 'ng7Detector',///readonly: true,///},///ng7MinimumQ': {///name: 'Minimum Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumQ': {///name: 'Maximum Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumVerticalQ': {///name: 'Maximum Vertical Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumHorizontalQ': {///name: 'Maximum Horizontal Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///"
    output = create_python_helper(var)
