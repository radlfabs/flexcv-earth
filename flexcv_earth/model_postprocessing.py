import logging
from pprint import pformat

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from neptune.types import File

logger = logging.getLogger(__name__)
mpl.use("Agg")
style_talk = "seaborn-talk"  # refer to plt.style.available


class EarthModelPostProcessor():
    def __init__(self):
        super().__init__()

    def __call__(self, results_all_folds, fold_result, features, run, *args, **kwargs):
        """Postprocessing function for the MARS model.
        Logs the parameters to Neptune.
        Creates a variable importance table and logs barplots to neptune.

        Args:
            results_all_folds: A dict of results for all folds
            fold_result: A dataclass containing the results for the current fold
            features: list of features
            run: neptune run object
            *args: any additional arguments
            **kwargs: any additional keyword arguments

        Returns:
            (dict): updated results dictionary
        """
        with plt.style.context("ggplot"):
            imp_df: pd.DataFrame = fold_result.best_model.get_variable_importance(features)
            run[f"{fold_result.model_name}/FeatImportance/Table"].append(File.as_html(imp_df))
            for col in imp_df.columns:
                # plot all rows of col where col is not 0
                fig = plt.figure()
                tmp = imp_df[col]
                tmp = tmp[tmp != 0]
                try:
                    tmp.plot.barh()
                    plt.title(f"{col} Variable Importance")
                    run[f"{fold_result.model_name}/FeatImportance/"].append(fig)
                except Exception as e:
                    logger.info(f"{e}")
                    logger.info(f"Could not make barplot for {fold_result.model_name}. Continuing.")
                del fig
                plt.close()

            run[f"{fold_result.model_name}/BestParams"].append(
                pformat(fold_result.best_params)
            )

        return results_all_folds


if __name__ == "__main__":
    pass
