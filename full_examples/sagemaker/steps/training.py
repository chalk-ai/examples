from sagemaker.workflow.function_step import step

PARAM_GRID = {
    'xgb__n_estimators': [20, 50, 100, 200],
    'xgb__learning_rate': [0.01, 0.1, 0.2],
    'xgb__max_depth': [3, 5, 7, 9],
}

@step(
    name="model-training",
    instance_type="ml.m5.xlarge",
    keep_alive_period_in_seconds=300,
)
def train(
    xtrain_path: str,
    ytrain_path: str,
    num_rounds: int
):
    from sklearn.pipeline import Pipeline
    import pandas as pd
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import RandomizedSearchCV

    # read data files from S3
    X_train = pd.read_parquet(xtrain_path)
    y_train = pd.read_parquet(ytrain_path)

    pipeline = Pipeline(
        steps=[
            ("impute", (SimpleImputer())),
            ("scaler", StandardScaler()),
            ("xgb", GradientBoostingClassifier()),
        ]
    )
    rsc = RandomizedSearchCV(
        pipeline,
        param_distributions=PARAM_GRID,
        n_iter=num_rounds,
        cv=3,
        scoring="f1",
        n_jobs=-1,
    )
    rsc.fit(X_train, y_train)

    return rsc.best_estimator_
