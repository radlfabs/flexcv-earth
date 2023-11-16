# Welcome to flexcv-earth

See our repository here: [flexcv-earth](https://github.com/radlfabs/flexcv-earth)

This python package provides wrapper classes for the `earth` function from the `earth` package in R.
It then can be used as a sklearn estimator in python and especially in the `flexcv` package.

## Installation

```bash
pip install flexcv_earth @ git+https://github.com/radlfabs/flexcv-earth
```

#### Additional dependencies of `rpy2`

The model class for the `EarthRegressor` is actually wrapping around `rpy2` code and is using embedded `R` under the hood. 
Therefore, you should have a recent `R` version installed and run our `install_rpackages.py` script. 
From the command line change your directory to your `flexcv-earth` installation directory. 
This can be your folder that you created with `venv`. Run our python script that installs the remaining R dependencies.

```bash
cd path/to/flexcv-earth/
python -m install_rpackages
```

Now you have installed everything you need to use the `EarthRegressor`with flexcv-earth.

## Use with flexcv

You can use `flexcv` to perform cross validation with the `EarthRegressor` class.
Define a model configuration with yaml as follows:

```python
from flexcv import CrossValidation
from flexcv_earth import EarthRegressor, EarthModelPostProcessor
from flexcv.synthesizer import generate_data

X, y, _, _ = generate_data(10, 100)

yaml_config = """
EarthRegressor:
    requires_inner_cv: True
    n_trials: 200
    allows_n_jobs: False
    model: EarthRegressor
    params:
        degree: !Int
            low: 1
            high: 5
        nprune: !Int
            low: 1
            high: 300
        fast_k: !Int
            low: 0
            high: 20
        newvar_penalty: !Float
            low: 0.01
            high: 0.2
    post_processor: EarthModelPostProcessor
    add_merf: True
"""

cv = (
    CrossValidation().set_data(X, y)
    .set_models(yaml_strin=yaml_config)
)
```

## Reference

::: flexcv_earth.models.EarthRegressor
    rendering:
        show_root_heading: false

::: flexcv_earth.model_postprocessing.EarthModelPostProcessor
    rendering:
        show_root_heading: false
