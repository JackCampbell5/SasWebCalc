/*
 * Debye model for simulating intensities
 */
function debye(params) {
    // params are: [0] scale factor, [1] radius of gyration [A], [2] background [cm-1], [3] q value [A^-1]

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

/*
 * Sphere model for simulating intensities
 */
function sphere(params) {
    // params are: [0] scale factor, [1] radius [A], [2] deltaRho [cm-1], [3] background [cm-1], [4] q value [A^-1]

    // calculates scale * f^2 / volume where f = volume * 3 * deltaRho * (sin(qr) - q*r*cos(qr)) / (q*r)^3
    var scale = params[0];
    var radius = params[1];
    var sldSphere = params[2] * 10e-6;
    var sldSolvent = params[3] * 10e-6;
    var bkg = params[4];
    var q = params[5];
    var deltaRho = sldSphere - sldSolvent;

    var radius_cubed = radius * radius * radius;
    var q_rad = q * radius;
    var deltaRhoSquared = deltaRho * deltaRho;

    if (q == 0) {
        return (4 / 3) * Math.PI * radius_cubed * deltaRhoSquared * scale * 1e8 + bkg;
    }

    var bessel = 3 * (Math.sin(q_rad) - q_rad * Math.cos(q_rad)) / (q_rad * q_rad * q_rad);
    var volume = 4 * Math.PI * radius_cubed / 3;
    var f = volume * bessel * deltaRho;

    var f_squared = (f * f / volume) * 1e8;

    // then add in the background
    return (f_squared * scale + bkg);
}
