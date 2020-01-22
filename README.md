# SASWEBCALC

*Active Work-In-Progress*
A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

Current features:
- Calculate estimated I vs. Q for 30m SANS (NG7 and NGB30) configurations
- Modify model parameters for the Debye or Sphere models to better estimate the scattering
- Freeze configuration/model combinations
- Plot I vs. Q of any number of configuration/model combinations
- 2D heatmap of I(Q) for the most recent calculation
- Send frozen configurations directly to the desired instrument

Features actively being worked on and known issues:
- 10m and VSANS not yet available
- Values loaded from instrument only used to populate wavelength spread (so far)
- Plotted slicers and calculations are not matching
- Plotted slicers often off scale of plot when detector is offset
- No incomplete gamma function available in javascript, so resolution calculations are not correct

Anticipated features:
- Option of inputting a Q range and model only, with no instrumental resolution calculations
- Model selection tool based off of [sasmodels] (https://github.com/SasView/sasmodels)