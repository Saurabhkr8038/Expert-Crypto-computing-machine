import os

# Define folder structure
structure = {
    "data/raw": [],
    "data/processed": [],
    "notebooks": [
        "01_data_collection.ipynb",
        "02_feature_engineering.ipynb",
        "03_model_training.ipynb",
        "04_backtesting.ipynb",
        "05_real_time_ai_signals.ipynb",
        "06_dashboard_and_api.ipynb"
    ],
    "src": [
        "data_loader.py",
        "feature_engineering.py",
        "model.py",
        "optuna_tuner.py",
        "backtest.py",
        "explainability.py",
        "ai_intelligence.py",
        "alerts.py",
        "scheduler.py"
    ],
    "dashboard/templates": ["index.html"],
    "dashboard/static": ["style.css"],
    "dashboard": ["app.py"],
    "reports": ["daily_signals.pdf"],
    "models": ["xgb_model.pkl"],
    "logs": ["execution_log.txt"]
}

# Create folders and files
base_path = "ai_crypto_trading_ai_project"
for folder, files in structure.items():
    folder_path = os.path.join(base_path, folder)
    os.makedirs(folder_path, exist_ok=True)
    if not files:
        # Create .gitkeep for empty folders
        open(os.path.join(folder_path, ".gitkeep"), "w").close()
    else:
        for file in files:
            open(os.path.join(folder_path, file), "w").close()

# Root-level files
root_files = ["README.md", "requirements.txt", ".env", "run.py"]
for file in root_files:
    open(os.path.join(base_path, file), "w").close()

print("✅ Project structure created successfully!")
