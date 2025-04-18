# src/explainability.py

import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt


def load_model(model_path):
    """
    Load a trained model (XGBoost, LightGBM, etc.) from disk.
    """
    print(f"[*] Loading model from: {model_path}")
    return joblib.load(model_path)


def explain_model(model, X_sample):
    """
    Run SHAP explainability on a tree-based model.
    X_sample: pd.DataFrame with sample input features.
    """
    print("[*] Generating SHAP explainer...")
    explainer = shap.Explainer(model)
    shap_values = explainer(X_sample)

    print("[✓] SHAP values computed.")
    return explainer, shap_values


def plot_summary(shap_values, X_sample, max_display=15):
    """
    Plot SHAP feature importance summary.
    """
    print("[*] Plotting SHAP summary...")
    plt.figure()
    shap.summary_plot(shap_values, X_sample, max_display=max_display)
    plt.show()


def plot_bar(shap_values, X_sample, max_display=15):
    """
    Bar plot version of SHAP feature importances.
    """
    print("[*] Plotting SHAP bar chart...")
    plt.figure()
    shap.plots.bar(shap_values, max_display=max_display)
    plt.show()


def explain_instance(model, X_sample, index=0):
    """
    Explain a specific prediction (index) using SHAP force plot.
    """
    explainer, shap_values = explain_model(model, X_sample)
    shap.initjs()
    print(f"[*] Explaining instance at index {index}")
    return shap.plots.force(shap_values[index])
