import unittest
import numpy as np
from numpy.testing import assert_array_equal
from sklearn.utils.estimator_checks import check_estimator
from flexcv_earth import EarthRegressor

class TestEarthRegressor(unittest.TestCase):
    def setUp(self):
        self.regressor = EarthRegressor(degree=2, random_state=42)
        self.X_train = np.random.rand(100, 5)
        self.y_train = np.random.rand(100)
        self.X_test = np.random.rand(10, 5)

    def test_fit(self):
        self.regressor.fit(self.X_train, self.y_train)
        self.assertTrue(self.regressor.is_fitted_)

    def test_predict(self):
        self.regressor.fit(self.X_train, self.y_train)
        y_pred = self.regressor.predict(self.X_test)
        self.assertEqual(y_pred.shape[0], self.X_test.shape[0])

    def test_get_params(self):
        params = self.regressor.get_params()
        expected_params = {
            "degree": 2,
            "nprune": None,
            "nk": None,
            "thresh": 0.001,
            "minspan": 0,
            "endspan": 0,
            "newvar_penalty": 0.0,
            "fast_k": 20,
            "fast_beta": 1.0,
            "pmethod": "backward",
            "random_state": 42,
        }
        self.assertEqual(params, expected_params)

    def test_variable_importance(self):
        self.regressor.fit(self.X_train, self.y_train)
        var_imp = self.regressor.get_variable_importance(['f1', 'f2', 'f3', 'f4', 'f5'])
        self.assertEqual(var_imp.shape[0], 5)

    def test_sklearn_compatibility(self):
        # Check compatibility with sklearn, it will raise an error if the estimator is not compatible
        check_estimator(EarthRegressor())

if __name__ == "__main__":
    unittest.main()