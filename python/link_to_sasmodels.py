import sasmodels.core as core
from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment

kernel = load_model('ellipsoid')

model = Model(kernel)

def get_all_models():
    core.__main__()