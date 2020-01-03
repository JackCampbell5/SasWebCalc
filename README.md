# SASWEBCALC

*Active Work-In-Progress*
A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

Current features:
- Calculate estimated I vs. Q for NG7 SANS configurations
- Modify model parameters for the Debye or Sphere models to better estimate the scattering
- Freeze configuration/model combinations
- Plot I vs. Q of any number of configuration/model combinations
- 2D heatmap of I(Q) for the most recent calculation
- Send frozen configurations directly to the desired instrument

Features actively being worked on and known issues:
- NG7 is the only instrument currently available
- Values loaded from instrument only used to populate wavelength spread (so far)
- No incomplete gamma function available in javascript, so resolution calculations are not correct

Anticipated features:
- Option of inputting a Q range and model only, with no instrumental resolution calculations
- Model selection tool based off of [sasmodels] (https://github.com/SasView/sasmodels)