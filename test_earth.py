
def merf_earth_regression():
    X, y, group, random_slopes = generate_regression(
        10, 100, n_slopes=1, noise_level=9.1e-2, random_seed=42
    )

    model_map = ModelMappingDict(
        {
            "Earth": ModelConfigDict(
                {
                    "requires_inner_cv": True,
                    "allows_n_jobs": False,
                    "allows_seed": True,
                    "n_jobs_cv": 1,
                    "model": EarthRegressor,
                    "params": {  # 'degree', 'endspan', 'fast_beta', 'fast_k', 'minspan', 'newvar_penalty', 'nk', 'nprune', 'pmethod', 'random_state', 'thresh'
                        "degree": optuna.distributions.IntDistribution(1, 5),
                    },
                    "post_processor": mp.EarthModelPostProcessor,
                }
            ),
        }
    )

    cv = CrossValidation()
    results = (
        cv.set_data(X, y, group, random_slopes)
        .set_models(model_map)
        .set_inner_cv(3)
        .set_splits(n_splits_out=3)
        .set_merf(add_merf_global=True, em_max_iterations=5)
        .perform()
        .get_results()
    )

    return np.mean(results["MERF(Earth)"]["folds_by_metrics"]["r2"])


def test_merf_earth():
    """Test if the mean r2 value of the random forest regression is exactly the same over time."""
    assert np.isclose([merf_earth_regression()], [0.03308048396566532])
