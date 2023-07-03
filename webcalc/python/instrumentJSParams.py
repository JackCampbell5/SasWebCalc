def create_js(name=None, default=None, type=None, unit=None, readonly=None, options=None,
              min=None, max=None, range_id=None, hidden=None, lower_limit=None, upper_limit=None):
    # Add to the correct category
    js_array = {}
    if min is not None and min != "":
        js_array["min"] = min
    if max is not None and max != "":
        js_array["max"] = max
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
    if type is not None and type != "":
        js_array["type"] = type
    if unit is not None and unit != "":
        js_array["unit"] = unit
    if readonly is not None and readonly != "":
        js_array["readonly"] = readonly
    if options is not None and options != "":
        js_array["options"] = options
    print(js_array)
    return js_array
    # Ones that are not none add to the array


def generate_js_array():
    output = {}
    output["ng7Sample"] = {"name": "Sample Area Settings"}
    output["ng7Wavelength"] = {"name": "Wavelength Settings"}
    output["ng7Collimation"] = {"name": "Collimation Settings"}
    output["ng7Detector"] = {"name": "Detector Settings"}
    output["ng7QRange"] = {"name": "Calculated Q Range"}
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
            print(value)
            if output[num][len(output[num]) - 1:] != ',' and output[num][len(output[num]) - 1:] != '(':
                output[num] = output[num] + "]"
            output[num] = output[num] + " " + value[:value.find(':')] + "=" + value[value.find(':') + 1:]
            print(" " + value[:value.find(':')] + "=" + value[value.find(':') + 1:])
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
        print(value)
        output[place] = value
    return output


if __name__ == '__main__':
    var = "instrument_params_local: {///ng7BeamStopSizes': {///options: [2.54, 5.08, 7.62, 10.16]///},///ng7SampleTable': {///name: 'Sample Table',///default: \"Chamber\",///type: \"select\",///options: [///Chamber',///Huber'///],///unit: '',///category: 'ng7Sample',///},///ng7WavelengthInput': {///name: 'Wavelength',///default: 6.0,///min: 4.8,///max: 20.0,///type: \"number\",///unit: 'nm;',///category: 'ng7Wavelength',///},///ng7WavelengthSpread': {///name: 'Wavelength Spread',///default: 13.9,///type: \"select\",///category: 'ng7Wavelength',///unit: '',///options: [9.7, 13.9, 15, 22.1],///},///ng7BeamFlux': {///name: 'Beam Flux',///default: '',///type: \"number\",///unit: 'n cm<sup>-2</sup> s<sup>-1</sup>',///category: 'ng7Wavelength',///readonly: true,///},///ng7FigureOfMerit': {///name: 'Figure of merit',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7Attenuators': {///name: 'Attenuators',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7AttenuationFactor': {///name: 'Attenuation Factor',///default: '',///type: \"number\",///unit: '',///category: 'ng7Wavelength',///readonly: true,///},///ng7GuideConfig': {///name: 'Guides',///default: 0,///type: \"select\",///category: 'ng7Collimation',///unit: '',///options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS'],///},///ng7SourceAperture': {///name: 'Source Aperture',///default: 1.43,///type: \"select\",///unit: 'cm',///category: 'ng7Collimation',///options: [1.43, 2.54, 3.81, 5.08],///},///ng7SampleAperture': {///name: 'Sample Aperture',///default: 0.500,///type: \"select\",///unit: 'inch',///category: 'ng7Collimation',///options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom'],///},///ng7CustomAperture': {///name: 'Aperture Diameter',///default: 13,///type: \"number\",///unit: 'mm',///category: 'ng7Collimation',///hidden: true,///},///ng7SSD': {///name: 'Source-To-Sample Distance',///default: 1627,///type: \"number\",///unit: 'cm',///category: 'ng7Collimation',///readonly: true,///},///ng7SDDInputBox': {///name: 'Detector Distance',///default: 100,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///},///ng7SDDDefaults': {///name: '',///default: 100,///type: \"range\",///category: 'ng7Detector',///range_id: 'ng7SDDDefaultRange',///unit: '',///lower_limit: 90,///upper_limit: 1532,///options: [100, 400, 1300, 1530],///},///ng7OffsetInputBox': {///name: 'Detector Offset',///default: 0,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///},///ng7OffsetDefaults': {///name: '',///default: 0,///type: \"range\",///category: 'ng7Detector',///range_id: 'ng7OffsetDefaultRange',///unit: '',///lower_limit: 0,///upper_limit: 25,///options: [0, 5, 10, 15, 20, 25],///},///ng7SDD': {///name: 'Sample-To-Detector Distance',///default: 100,///type: \"number\",///unit: 'cm',///category: 'ng7Detector',///readonly: true,///},///ng7BeamDiameter': {///name: 'Beam Diameter',///default: '',///type: \"number\",///unit: \"cm\",///category: 'ng7Detector',///readonly: true,///},///ng7BeamStopSize': {///name: 'Beam Stop Diameter',///default: '',///type: \"number\",///unit: \"cm\",///category: 'ng7Detector',///readonly: true,///},///ng7MinimumQ': {///name: 'Minimum Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumQ': {///name: 'Maximum Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumVerticalQ': {///name: 'Maximum Vertical Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///ng7MaximumHorizontalQ': {///name: 'Maximum Horizontal Q',///default: '',///type: \"number\",///unit: \"Å;<sup>-1</sup>\",///category: 'ng7QRange',///readonly: true,///},///"
    output = create_python_helper(var)
