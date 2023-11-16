import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from flexcv_earth.model_postprocessing import EarthModelPostProcessor

class TestEarthModelPostProcessor(unittest.TestCase):
    def setUp(self):
        self.postprocessor = EarthModelPostProcessor()
        self.results_all_folds = {}
        self.features = ['f1', 'f2', 'f3', 'f4', 'f5']
        self.run = Mock()
        self.fold_result = Mock()
        self.fold_result.best_model.get_variable_importance.return_value = pd.DataFrame(np.random.rand(5, 5), columns=self.features)
        self.fold_result.best_model_name = 'EarthRegressor'
        self.fold_result.best_params = {'degree': 2, 'nprune': None}

    @patch('flexcv_earth.model_postprocessing.plt')
    @patch('flexcv_earth.model_postprocessing.File')
    def test_call(self, mock_file, mock_plt):
        mock_file.as_html.return_value = 'html_content'
        updated_results = self.postprocessor(self.results_all_folds, self.fold_result, self.features, self.run)
        self.assertEqual(updated_results, self.results_all_folds)
        self.run.__setitem__.assert_any_call('MARS/FeatImportance/Table', mock_file.as_html())
        self.run.__setitem__.assert_any_call(f"{self.fold_result.model_name}/BestParams", self.fold_result.best_params)

if __name__ == "__main__":
    unittest.main()