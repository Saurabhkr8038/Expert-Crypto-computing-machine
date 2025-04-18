# xgb_model_training.py

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load your dataset (assuming you've preprocessed your features and labels)
# Example: Load the preprocessed features (X) and target labels (y)
# You should replace this with your actual dataset (e.g., crypto data).
df = pd.read_csv('path_to_your_processed_data.csv')

# Define your features (X) and target (y)
# Example: X could be your technical indicators and sentiment scores, and y would be the Buy/Sell/Hold signals
X = df.drop(columns=['target'])  # Features: exclude target column
y = df['target']  # Target: Buy/Sell/Hold signals

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Instantiate and train the XGBoost model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model's performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of the XGBoost model: {accuracy * 100:.2f}%")

# Save the trained model as a .pkl file
joblib.dump(model, 'xgb_model.pkl')

print("XGBoost model saved as 'xgb_model.pkl'")
