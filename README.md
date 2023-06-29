# SASWEBCALC

*Active Work-In-Progress*
A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.

## Getting set up

The latest iteration runs using python Flask. To run saswebcalc from source, create a python environment using python 3.7 or higher and install all dependencies
 - Using a [python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)::

       $ python -m venv saswebcalc
       $ .\saswebcalc\Scripts\activate (Windows) -or- source saswebcalc/bin/activate (Mac/Linux)
       (saswebcalc) $ python -m pip requirements.txt
       (saswebcalc) $ python /path/to/saswebcalc/webcalc.py <port>
 
 - Using [miniconda](https://docs.conda.io/en/latest/miniconda.html)
or [anaconda](https://www.anaconda.com/)::
   
       $ conda create -n saswebcalc
       $ conda activate saswebcalc
       (saswebcalc) $ python -m pip requirements.txt
       (saswebcalc) $ python /path/to/saswebcalc/webcalc.py <port>

## References
- [Flow diagram of code](https://mm.tt/map/2428513537)

## Feature Set, Current and Planned

### Current features:
- Calculate estimated I vs. Q based on the SANS instrument configurations
- Select and modify form factor model parameters to estimate scattering using a model selection tool based off of [sasmodels](https://github.com/SasView/sasmodels)
- Freeze configuration/model combinations
- Plot I vs. Q for any number of configuration/model combinations with or without offsetting values
- Plot a 2D heatmap of I(Q) for the most recent calculation
- Inline help files and documentation
- Bug submission tool
- Selecting a structure factor@form factor for calculations
- Layered models now add additional layers when the number is changed
- User Defined Q-Range and Resolution fully working

### Features and issues actively being worked on for v1.0:
- Only circular averaging is working until the following issues can be fixed with other averaging types
 - Plotted slicers and calculations do not match
 - Plotted slicers sometimes off scale of plot causing plot region to expand
- VSANS instrument with both a 1D and 2D data representation

### Anticipated features:
- Enable polydispersity and magnetic calculations (v1.2)
- Allow user to enter sample thickness, transmission, and counting time (v1.2)
- Send frozen configurations directly to the desired instrument (v1.3)
- Call instrument server to load real instrument values (v1.3)
- Optimize suggested counting time using [molgroups](https://github.com/criosx/molgroups) (v1.4)
