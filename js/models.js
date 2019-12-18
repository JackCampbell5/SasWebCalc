/*
 * Debye model for simulating intensities
 */
function debye(params) {
    // params are:
    //[0] scale factor
    //[1] radius of gyration [A]
    //[2] background	[cm-1]
    //[3] q value [A^-1]

    // calculates (scale*debye)+bkg
    var scale = params[0];
    var rg = params[1];
    var bkg = params[2];
    var q = params[3];
    var qrSquared = (q * rg) * (q * rg);
    var pOfQ = 2 * (Math.exp(-1 * qrSquared) - 1 + qrSquared) / Math.pow(qrSquared, 2);

    //scale
    pOfQ *= scale;
    // then add in the background
    return (pOfQ + bkg);
}
