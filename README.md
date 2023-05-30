# SASWEBCALC

*Active Work-In-Progress*
A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

## Getting set up

The latest iteration runs using python Flask. To run saswebcalc from source, create a python environment using python 3.7 or higher and install all dependencies
 - Using a [python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)::

       $ python -m venv saswebcalc
       $ .\saswebcalc\Scripts\activate (Windows) -or- source saswebcalc/bin/activate (Mac/Linux)
       (saswebcalc) $ python -m pip install numpy flask
       (saswebcalc) $ python /path/to/saswebcalc/webcalc.py <port>
 
 - Using [miniconda](https://docs.conda.io/en/latest/miniconda.html)
or [anaconda](https://www.anaconda.com/)::
   
       $ conda create -n saswebcalc -c conda-forge numpy flask
       $ conda activate saswebcalc
       (saswebcalc) $ python /path/to/saswebcalc/webcalc.py <port>

## References
- [Flow diagram of code](https://mm.tt/map/2428513537)
## Feature Set, Current and Planned

### Current features:
- Calculate estimated I vs. Q for standard SANS instrument configurations
- Modify model parameters for the Debye or Sphere models to better estimate the scattering
- Freeze configuration/model combinations
- Plot I vs. Q of any number of configuration/model combinations
- 2D heatmap of I(Q) for the most recent calculation
- Send frozen configurations directly to the desired instrument

## Features actively being worked on and known issues:
- Values loaded from instrument only used to populate wavelength spread (so far)
- Only circular averaging is available until the following issues can be fixed with other averaging types
 - Plotted slicers and calculations do not match
 - Plotted slicers often off scale of plot when detector is offset
 - Calculated Q values for non-circular averaging methods not correct
- No incomplete gamma function available in javascript, so resolution calculations are not correct

## Anticipated features:
- Option of inputting a Q range and model only, with no instrumental resolution calculations
- Model selection tool based off of [sasmodels] (https://github.com/SasView/sasmodels)

