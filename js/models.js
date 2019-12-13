/*
 * Debye model for simulating intensities
 */
function debye(params) {
    // variables are:
    //[0] scale factor
    //[1] radius of gyration [A]
    //[2] background	[cm-1]

    // calculates (scale*debye)+bkg
    var scale = params[0];
    var rg = params[1];
    var bkg = params[2];
    for (var i = 0; i < window.qValues.length; i++) {
        var qrSquared = (window.qValues[i] * rg) ^ 2;
        var pOfQ = 2 * (Math.exp(-1 * qrSquared) - 1 + qrSquared) / Math.pow(qrSquared, 2);

        //scale
        pOfQ *= scale;
        // then add in the background
        window.aveIntensity[i] = pOfQ + bkg;
    }
}
