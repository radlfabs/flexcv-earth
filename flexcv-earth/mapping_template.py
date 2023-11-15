mapping = {
    "EarthRegressor": ModelConfigDict(
        {
            "requires_inner_cv": True,
            "n_trials": 200,
            "allows_n_jobs": False,
            "model": EarthRegressor,
            "params": {  # 'degree', 'endspan', 'fast_beta', 'fast_k', 'minspan', 'newvar_penalty', 'nk', 'nprune', 'pmethod', 'random_state', 'thresh'
                "degree": optuna.distributions.IntDistribution(1, 5),
                "nprune": optuna.distributions.IntDistribution(1, 300),
                # "fast_k": optuna.distributions.CategoricalDistribution([0, 1, 5, 10, 20]),  #
                "fast_k": optuna.distributions.IntDistribution(0, 20),  #
                # "nk": does not help
                "newvar_penalty": optuna.distributions.FloatDistribution(0.01, 0.2),
                # "pmethod": # use default: backward
                # "fast_beta": # default(=1) yielded best results
            },
            "post_processor": mp.EarthRegressor,
            "add_merf": True,
        }
)
}