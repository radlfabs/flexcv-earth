# flexcv-earth

This is a additional package for the python package [flexcv](https://github.com/radlfabs/flecv).
`flexcv-earth` provides a wrapper class to use Earth model regression in python without the need to install `pyearth`.
Instead, `flexcv-earth` uses the `rpy2` package to call the `earth` function from the `earth` package in R.

## Installation
Make sure to have Python 3.10 or 3.11 installed. Also, you will need to install R
```
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
