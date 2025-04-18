# src/model.py

import pandas as pd
import numpy as np
import joblib
import optuna
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier


class CryptoModelTrainer:
    def __init__(self, df: pd.DataFrame, target_column='target'):
        self.df = df.dropna()
        self.target_column = target_column
        self.model = None

    def prepare_data(self):
        print("[+] Preparing training and test data...")
        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_xgboost(self, use_optuna=False):
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        if use_optuna:
            print("[*] Running Optuna tuning for XGBoost...")
            def objective(trial):
                params = {
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'subsample': trial.suggest_float('subsample', 0.5, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
                    'gamma': trial.suggest_float('gamma', 0, 5),
                }
                model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', **params)
                score = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy').mean()
                return score

            study = optuna.create_study(direction="maximize")
            study.optimize(objective, n_trials=30)
            best_params = study.best_params
            print(f"[✓] Best params: {best_params}")
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', **best_params)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')

        print("[+] Training XGBoost model...")
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        print(classification_report(y_test, y_pred))
        return self.model

    def train_lightgbm(self):
        X_train, X_test, y_train, y_test = self.prepare_data()
        print("[+] Training LightGBM model...")
        self.model = LGBMClassifier()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        print(classification_report(y_test, y_pred))
        return self.model

    def predict(self, new_data: pd.DataFrame):
        if self.model is None:
            raise ValueError("Model is not trained. Call train_xgboost or train_lightgbm first.")
        return self.model.predict(new_data)

    def save_model(self, filepath: str = 'models/xgb_model.pkl'):
        if self.model:
            joblib.dump(self.model, filepath)
            print(f"[✓] Model saved to {filepath}")
        else:
            print("[!] No model to save.")

    def load_model(self, filepath: str = 'models/xgb_model.pkl'):
        self.model = joblib.load(filepath)
        print(f"[✓] Model loaded from {filepath}")
        return self.model


if __name__ == "__main__":
    df = pd.read_csv("data/processed/btc_features.csv", index_col='timestamp', parse_dates=True)
    
    # Example: assume we already have Buy/Sell/Hold targets in 'target' column
    trainer = CryptoModelTrainer(df, target_column='target')
    model = trainer.train_xgboost(use_optuna=True)
    trainer.save_model()
