# SASWEBCALC

A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

Current features:

- Calculate estimated I vs. Q for NG7 SANS configurations
- Modify model parameters for the Debye or Sphere models to better estimate the scattering
- Freeze configuration/model combinations
- Plot I vs. Q of any number of configuration/model combinations
- 2D heatmap of I(Q) for the most recent calculation
- Configurations can be sent directly to the desired instrument

Known issues:

- NG7 is the only instrument currently available
- No incomplete gamma function available in javascript, so resolution calculations are not correct=

Anticipated features:

- Option of inputting a Q range and model only, with no instrumental resolution calculations
- Ability to read instrumental values directly from the SAS instrument
- Model selection tool based off of [sasmodels] (https://github.com/SasView/sasmodels)