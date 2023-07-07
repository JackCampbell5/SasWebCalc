"""
This module contains all the necessary functions to create a value encoded for a js element and restructure and change
that dictionary as necessary
"""


def create_js(name=None, default=None, type_val=None, unit=None, readonly=None, options=None, step=None, range_id=None,
              hidden=None, lower_limit=None, upper_limit=None):
    """Takes in the appropriate parameters to set up the js dictionary from either a function with pre encoded
    defaults or just parameters passed in by a direct call to this function

    Sets all other parameters to the default or None and then runs them through create_js to create the dictionary
    :param str name: The name of the parameter
    :param any default: The default value of the parameter
    :param str type_val: The type of vue object to use for the parameter
    :param str unit: The unit of the parameter
    :param boolean readonly: The boolean that decides whether this parameter editable by the user
    :param list options: The options for the parameter if it needs specific options
    :param str range_id: The id of the range of the range
    :param boolean hidden: The boolean that decides whether this parameter is hidden at start
    :param float lower_limit: The lower limit if the parameter is a range
    :param float upper_limit: The upper limit is the parameter is a range
    :returns: The JS dictionary of params encoded for js
    :rtype: Dict
    """
    # Add to the correct category
    js_array = {}
    if step is not None and step != "":
        js_array["step"] = step
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
    return js_array  # Ones that are not none add to the array


def create_sample_table(name='Sample Table', default='Chamber', type_val='select', unit='', readonly=None, options=None,
                        hidden=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = ['Chamber', 'Huber']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     hidden=hidden)


def create_wavelength_input(name='Wavelength', default=6.0, type_val='number', unit='nm;', readonly=None, options=None,
                            step=None, hidden=None, range_id=None, lower_limit=4.8, upper_limit=20.0):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit, hidden=hidden)


def create_wavelength_spread(name='Wavelength Spread', default=13.9, type_val='select', unit='', readonly=None,
                             options=None, hidden=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [9.7, 13.9, 15, 22.1]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     hidden=hidden)


def create_beam_flux(name='Beam Flux', default='', type_val='number', unit='n cm<sup>-2</sup> s<sup>-1</sup>',
                     readonly=True, options=None, step=None, hidden=None, range_id=None, lower_limit=None,
                     upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_figure_of_merit(name='Figure of Merit', default='', type_val='number', unit='', readonly=True, options=None,
                           step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_attenuators(name='Attenuators', default='', type_val='number', unit=None, readonly=True, options=None,
                       step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_attenuation_factor(name='Attenuation Factor', default='', type_val='number', unit=None, readonly=True,
                              options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_guide_config(name='Guides', default=0, type_val='select', unit=None, readonly=None, options=None,
                        hidden=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     hidden=hidden)


def create_source_aperture(name='Source Aperture', default=1.43, type_val='select', unit='cm', readonly=None,
                           options=None, hidden=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [1.43, 2.54, 3.81, 5.08]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     hidden=hidden)


def create_sample_aperture(name='Sample Aperture', default=0.500, type_val='select', unit='inch', readonly=None,
                           options=None, hidden=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom']
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     hidden=hidden)


def create_custom_aperture(name='Aperture Diameter', default=13, type_val='number', unit='mm', readonly=None,
                           options=None, step=None, hidden=True, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_ssd(name='Source-To-Sample Distance', default=1627, type_val='number', unit='cm', readonly=True,
               options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_sdd_input_box(name='Detector Distance', default=100, type_val='number', unit='cm', readonly=None,
                         options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_sdd_defaults(name=' ', default=100, type_val='range', unit='', readonly=None, options=None,
                        range_id='ng7SDDDefaultRange', hidden=None, lower_limit=90, upper_limit=1532):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [100, 400, 1300, 1530]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     range_id=range_id, hidden=hidden, lower_limit=lower_limit, upper_limit=upper_limit)


def create_offset_input_box(name='Detector Offset', default=0, type_val='number', unit='cm', readonly=None,
                            options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_offset_defaults(name=' ', default=0, type_val='range', unit='', readonly=None, options=None,
                           range_id='ng7OffsetDefaultRange', hidden=None, lower_limit=0, upper_limit=25):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    if options is None: options = [0, 5, 10, 15, 20, 25]
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     range_id=range_id, hidden=hidden, lower_limit=lower_limit, upper_limit=upper_limit)


def create_sdd(name='Sample-To-Detector Distance', default=100, type_val='number', unit='cm', readonly=True,
               options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_beam_diameter(name='Beam Diameter', default='', type_val='number', unit='cm', readonly=True, options=None,
                         step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_beam_stop_size(name='Beam Stop Diameter', default='', type_val='number', unit='cm', readonly=True,
                          options=None, step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_min_q(name='Minimum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True, options=None,
                 step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_max_q(name='Maximum Q', default='', type_val='number', unit='Å;<sup>-1</sup>', readonly=True, options=None,
                 step=None, hidden=None, range_id=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_max_vertical_q(name='Maximum Vertical Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                          readonly=True, options=None, step=None, hidden=None, range_id=None, lower_limit=None,
                          upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_maximum_horizontal_q(name='Maximum Horizontal Q', default='', type_val='number', unit='Å;<sup>-1</sup>',
                                readonly=True, options=None, step=None, hidden=None, range_id=None, lower_limit=None,
                                upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, hidden=hidden, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit)


def create_number_input(name=None, default=0.0, type_val='number', unit='Å', readonly=None, options=None, step=None,
                        range_id=None, hidden=None, lower_limit=None, upper_limit=None):
    """Function that creates a js element based on the parameters given(All parameters are defined in create JS)

    :returns: A dictionary of parameters encoded by create js
    """
    return create_js(name=name, default=default, type_val=type_val, unit=unit, readonly=readonly, options=options,
                     step=step, range_id=range_id, lower_limit=lower_limit, upper_limit=upper_limit, hidden=hidden)


def encode_secondary_elements(more_data=None, ssd=True, offset=True):
    """Checks if the element changed is a key in the dictionary and then changed values based on the dictionary in
    result[key]


    The output of this function will be  in the form of result[paramName] = {"cat1": "", "name1": "", "cat2": "",
    "name2": ""}

    + paramName - the name of the element in the js that if changed the code will run

    + cat - the category that the parameter in name is under

    + name - the name of the parameter

    In the JavScript it will check for if the element changed was paramName and if so it will set cat1[name1].value =
    cat2[value2].value


    :param dict more_data: More data in dictionary form to add if more values need to be updated simultaneously
    :param boolean ssd: Whether ssd secondary element data is necessary(Defaults to True)
    :param boolean offset: Whether offset secondary element data is necessary(Defaults to True)
    :return: A dictionary containing the values
    """
    if more_data is not None:
        result = more_data
    else:
        result = {}
    if ssd:
        result["sDDInputBox"] = {"cat1": "Detector", "name1": "sDDDefaults", "cat2": "Detector", "name2": "sDDInputBox"}
        result["sDDDefaults"] = {"cat1": "Detector", "name1": "sDDInputBox", "cat2": "Detector", "name2": "sDDDefaults"}
    if offset:
        result["offsetInputBox"] = {"cat1": "Detector", "name1": "offsetDefaults", "cat2": "Detector",
                                    "name2": "offsetInputBox"
                                    }
        result["offsetDefaults"] = {"cat1": "Detector", "name1": "offsetInputBox", "cat2": "Detector",
                                    "name2": "offsetDefaults"
                                    }
    return result


def check_params(params=None):
    """Goes thought the dictionary provided and if any of the category sub dictionary only have one value(name) they
    are removed as they do not contain any js elements

    :param dict params: The dictionary of category's to check over
    :return: The corrected dictionary of category with unneeded ones removed
    :rtype: Dict
    """
    if params is None: params = None
    return_array = params.copy()
    for name in params.keys():
        if len(params[name]) < 2 and name != "hidden":
            return_array.pop(name)
    return return_array


def generate_js_array(name=True):
    """Generates a dictionary of category's each containing a name parameter in string form if Name is True

    :param boolean name: Adds the name to each dictionary(Default is True)
    :return: A dictionary containing output[category] = {"name": theName}
    :rtype: Dict
    """
    output = {}
    output["Sample"] = {"name": "Sample Area Settings"} if name else {}
    output["Wavelength"] = {"name": "Wavelength Settings"} if name else {}
    output["Collimation"] = {"name": "Collimation Settings"} if name else {}
    output["Detector"] = {"name": "Detector Settings"} if name else {}
    output["QRange"] = {"name": "Calculated Q Range"} if name else {}
    output["hidden"] = {"secondary_elements": {}}
    return output
