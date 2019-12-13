# SASWEBCALC

A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

Current features:

- Calculate I vs. Q for NG7 SANS configurations using the Debye model
- Freeze configuration/model combinations
- Plot I vs. Q of any number of configuration/model combinations
- 2D heatmap of I(Q) = 1 for all Q

Known issues:

- Freeze/clear buttons not always shown
- NG7 is the only instrument currently available
- No incomplete gamma function in javascript, so oscillations introduced into data
- Model and resolutions not applied to 2D heatmap, so all intensities are 1

Anticipated features:

- Instrument selection tool for NIST center for neturon research instruments
	- Option of inputting a Q range and model only, with no instrumental resolution calculations
- Theoretical 1D and 2D scattering plots, including instrumetal effects, if known
- Ability to freeze any number of configuration/model combinations for direct 1D comparisons
- Ability to send frozen configurations directly to the desired instrument
- Ability to read instrumental values directly from the SAS instrument
- Model selection tool based off of [sasmodels] (https://github.com/SasView/sasmodels)
- Modify model parameters to better tune and plan for an experiment