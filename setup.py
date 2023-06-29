from setuptools import setup, find_packages

setup(
    name='SasWebCalc',
    version='1.0.0',
    url='https://gitlab.nist.gov/gitlab/jkrzywon/saswebcalc.git',
    author='Jeffery Krzywon and Jack Campbell',
    author_email='jeffery.krzywon@nist.gov',
    description='A web-based small-angle scattering (SAS) tool for calculating theoretical I vs. Q and 2D scattering patterns based off an instrumental configuration and SAS model.',
    packages=find_packages(),
    install_requires=['numpy', 'flask', 'sasmodels', 'gunicorn'],
)