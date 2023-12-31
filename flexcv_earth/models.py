import gc
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri, pandas2ri
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted

np.random.seed(42)
logger = logging.getLogger(__name__)


class EarthRegressor(BaseEstimator, RegressorMixin):
    """Wrapper Class for Earth Regressor in R.
    For more Details see https://cran.r-project.org/web/packages/earth/earth.pdf.

    Args:
        degree (int): Degree of the splines. 1 for linear, 2 for quadratic, etc. (Default value = 1)
        nprune (int | None): Number of pruning steps. If None, the number of pruning steps is determined by the algorithm. (Default value = None)
        nk (int | None): Number of knots. If None, the number of knots is determined by the algorithm. The default is semi-automatically calculated from the number of predictors but may need adjusting. (Default value = None)
        thresh (float): Forward stepping threshold. (Default value = 0.001)
        minspan (int): Minimum number of observations between knots. (Default value = 0)
        endspan (int): Minimum number of observations before the first and after the final knot. (Default value = 0)
        newvar_penalty (float): (Default value = 0.0)
        fast_k (int): Maximum number of parent terms considered at each step of the forward pass. (Default value = 20)
        fast_beta (float): Fast MARS ageing coefficient, as described in the Fast MARS paper section 3.1. Default is 1. A value of 0 sometimes gives better results. (Default value = 1.0)
        pmethod (str): Pruning method. One of: backward none exhaustive forward seqrep cv. Default is "backward". Specify pmethod="cv" to use cross-validation to select the number of terms. This selects the number of terms that gives the maximum mean out-of-fold RSq on the fold models. Requires the nfold argument. Use "none" to retain all the terms created by the forward pass. If y has multiple columns, then only "backward" or "none" is allowed. Pruning can take a while if "exhaustive" is chosen and the model is big (more than about 30 terms). The current version of the leaps package used during pruning does not allow user interrupts (i.e., you have to kill your R session to interrupt; in Windows use the Task Manager or from the command line use taskkill). (Default value = "backward")

    """

    def __init__(
        self,
        degree: int = 1,
        nprune: int = None,
        nk: int = None,
        thresh: float = 0.001,
        minspan: int = 0,
        endspan: int = 0,
        newvar_penalty: float = 0.0,
        fast_k: int = 20,
        fast_beta: float = 1.0,
        pmethod: str = "backward",
        random_state: int = None,
    ):
        self.degree = degree
        self.nprune = nprune
        self.nk = nk
        self.thresh = thresh
        self.minspan = minspan
        self.endspan = endspan
        self.newvar_penalty = newvar_penalty
        self.fast_k = fast_k
        self.fast_beta = fast_beta
        self.pmethod = pmethod
        self.random_state = random_state

    def fit(self, X, y):
        """Fit a EARTH model to the given training data.

        Args:
          X (array-like): Features.
          y (array-like): Target values.

        Returns:
           (object): Returns self.
        """
        if np.iscomplexobj(X) or np.iscomplexobj(y):
            raise ValueError("Complex data not supported")
        # ro.r('sink(nullfile())')
        if self.random_state is not None:
            ro.r(f"set.seed({self.random_state})")

        ro.r(
            """
            library(earth)
        """
        )
        numpy2ri.activate()
        pandas2ri.activate()

        assert (
            X.shape[0] == y.shape[0]
        ), "Number of X samples must match number of y samples."

        # Convert X, y according to its type
        if isinstance(X, pd.DataFrame):
            # Convert pandas dataframe to R dataframe
            r_X = pandas2ri.py2rpy(X)
        elif isinstance(X, np.ndarray):
            r_X = numpy2ri.numpy2rpy(X)
            # Convert numpy array to R matrix
        else:
            r_X = ro.r.matrix(X, nrow=X.shape[0], ncol=X.shape[1])

        # Convert pandas Series to R vector
        r_y = ro.FloatVector(y)

        # Fit MARS regression model using earth function from the earth package
        # make nprune None in R as default
        nprune = self.nprune if self.nprune is not None else ro.r("as.null")()
        # The following has a special defaults which we dont want to overwrite with None
        nk = {"nk": self.nk} if self.nk is not None else {}
        # We have to pass newvar.penalty as a named argument because Python does not allow "." in variable names
        newvar_penalty = {"newvar.penalty": self.newvar_penalty}
        fast_k = {"fast.k": self.fast_k}
        fast_beta = {"fast.beta": self.fast_beta}

        self.model_ = ro.r.earth(
            r_X,
            r_y,
            degree=self.degree,
            nprune=nprune,
            thresh=self.thresh,
            minspan=self.minspan,
            endspan=self.endspan,
            pmethod=self.pmethod,
            **newvar_penalty,
            **fast_k,
            **fast_beta,
            **nk,
        )

        self.is_fitted_ = True
        self.var_imp_ = self.calc_variable_importance()

        del r_X
        del r_y
        numpy2ri.deactivate()
        pandas2ri.deactivate()

        gc.collect()
        ro.r("gc()")
        gc.collect()

        return self

    def predict(self, X):
        """Make predicitons using the fitted model.

        Args:
          X (array-like): Features

        Returns:
            (array-like): An array of fitted values.
        """
        if np.iscomplexobj(X):
            raise ValueError("Complex data not supported")
        ro.r(
            """
            library(earth)
        """
        )
        numpy2ri.activate()
        pandas2ri.activate()
        # input checks
        check_is_fitted(self)
        if isinstance(X, pd.DataFrame):
            # Convert pandas dataframe to R dataframe
            r_X = pandas2ri.py2rpy(X)
        elif isinstance(X, np.ndarray):
            r_X = numpy2ri.numpy2rpy(X)
            # Convert numpy array to R matrix
        else:
            r_X = ro.r.matrix(X, nrow=X.shape[0], ncol=X.shape[1])
        # assign model in R in order to predict
        # ro.r.assign("model", self.model)
        y_pred = np.asarray(ro.r["predict"](self.model_, r_X))
        # make sure that the output is a 1d array
        y_pred = y_pred.ravel()
        del r_X

        numpy2ri.deactivate()
        pandas2ri.deactivate()
        gc.collect()
        ro.r("gc()")
        gc.collect()

        return y_pred

    def __sklearn_is_fitted__(self):
        return self.is_fitted_

    def get_params(self, deep=False):
        """Returns the parameters of the model.

        Args:
          deep: bool: This argument is not used.  (Default value = False)
        Returns:
            (dict): Parameter names mapped to their values.
        """
        return {
            "degree": self.degree,
            "nprune": self.nprune,
            "nk": self.nk,
            "thresh": self.thresh,
            "minspan": self.minspan,
            "endspan": self.endspan,
            "newvar_penalty": self.newvar_penalty,
            "fast_k": self.fast_k,
            "fast_beta": self.fast_beta,
            "pmethod": self.pmethod,
            "random_state": self.random_state,
        }

    def get_rmodel(self):
        """Returns the R model object.

        Returns:
            (object): The R model object."""
        return self.model_

    def make_r_plots(self):
        """Creates plots of the model in R and saves them to disk. They are saved to disk in the `tmp_imgs` folder."""
        Path("tmp_imgs").mkdir(parents=True, exist_ok=True)
        for i in range(1, 5):
            ro.r["png"](f"tmp_imgs/mars_plot_{i}.png", width=1024, height=1024)
            ro.r["plot"](self.model_, which=i)
            ro.r["dev.off"]()

    def calc_variable_importance(self):
        """Calculates the variable importance of the model.

        Returns:
            (pandas.DataFrame): A DataFrame containing the variable importance."""
        ro.globalenv["ev"] = ro.r["evimp"](self.model_, trim=False)
        imp = ro.r("as.data.frame(unclass(ev[,c(3,4,6)]))")
        imp_df: pd.DataFrame = ro.conversion.rpy2py(imp)
        imp_df.columns = ["nsubsets", "gcv", "rss"]

        del imp
        gc.collect()
        ro.r("rm(ev)")
        ro.r("gc()")
        gc.collect()
        return imp_df

    def get_variable_importance(self, features):
        """Returns the variable importance of the model.

        Args:
          features: array-like: The feature names.

        Returns:
            (pandas.DataFrame): A DataFrame containing the variable importance.
        """
        self.var_imp_.index = features
        return self.var_imp_


if __name__ == "__main__":
    pass
