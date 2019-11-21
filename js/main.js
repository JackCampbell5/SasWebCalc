// Your code here
function changeInstrument(instrument, generalSANS, VSANS) {
    var inst = document.getElementById(instrument)
    var genSANS = document.getElementById(generalSANS)
    var vSANS = document.getElementById(VSANS)
    var selectStr = inst.options[inst.selectedIndex].value;
    if (selectStr === "VSANS") {
        vSANS.style.display = "block";
        genSANS.style.display = "none";
    } else if (selectStr === "NGB30m" || selectStr === "NGB10m" || selectStr === "NG7") {
        genSANS.style.display = "block";
        vSANS.style.display = "none";
    } else {
        genSANS.style.display = "none";
        vSANS.style.display = "none";
    }
}
