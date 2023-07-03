def create_js_params(instrument_name="", instrument_object=None):
    # Loop though all the params
    # Add to the correct category
    instrument_object.get_js_params()
    # Ones that are not none add to the array


def create_python_helper():
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
                output[num] = output[num] + ")\n"
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
                    value[value.find('['):val_num] + value[value.find("'", value.find("'", val_num)) + 1:]
        output[place] = value
