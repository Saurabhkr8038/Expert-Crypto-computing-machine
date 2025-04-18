# src/optuna_tuner.py

import optuna
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier


def tune_model(X, y, model_type='xgboost', n_trials=30, scoring='accuracy'):
    print(f"[*] Starting Optuna tuning for {model_type.upper()}...")

    def objective(trial):
        if model_type == 'xgboost':
            params = {
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
                'gamma': trial.suggest_float('gamma', 0, 5),
            }
            model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', **params)

        elif model_type == 'lightgbm':
            params = {
                'num_leaves': trial.suggest_int('num_leaves', 20, 100),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            }
            model = LGBMClassifier(**params)

        elif model_type == 'random_forest':
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 5, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 4),
            }
            model = RandomForestClassifier(**params)

        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        score = cross_val_score(model, X, y, cv=3, scoring=scoring).mean()
        return score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    print(f"[✓] Best {model_type.upper()} params: {study.best_params}")
    return study.best_params, study.best_value
