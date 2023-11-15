"""This module implements a wrapper class for the Earth Regressor from R. `rpy2` is used to call the R functions from Python.

Author: Fabian Rosenthal
"""

from .models import EarthRegressor
from .model_postprocessing import EarthModelPostProcessor
