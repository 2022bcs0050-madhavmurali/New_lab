import pandas as pd
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
STUDENT_NAME = "Madhav Murali"
ROLL_NUMBER = "2022BCS0050"

# Experiment settings
TEST_SIZE = 0.3
RANDOM_STATE = 42
MODEL_TYPE = "LinearRegression"  # Options: "LinearRegression", "Lasso", "Ridge"
ALPHA = 0.2 # Only used for Lasso/Ridge

# ---------------------------------------------------------
# 1. Path Setup & Data Loading
# ---------------------------------------------------------
# Get the directory where THIS script (train.py) is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to this script
# Go up one level (..) from src to root, then into data/
data_path = os.path.join(current_dir, '..', 'data', 'winequality-red.csv')
# Go up one level (..) from src to root, then into models/
models_dir = os.path.join(current_dir, '..', 'models')

print(f"Loading data from: {data_path}")
print(f"Saving models to: {models_dir}")

# Load Data
try:
    df = pd.read_csv(data_path, sep=';')
except FileNotFoundError:
    print(f"Error: Could not find file at {data_path}")
    print("Please check if 'data/winequality-red.csv' exists in your repo structure.")
    exit(1)

X = df.drop('quality', axis=1)
y = df['quality']

# ---------------------------------------------------------
# 2. Pre-processing & Split
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------
# 3. Model Training
# ---------------------------------------------------------
if MODEL_TYPE == "LinearRegression":
    model = LinearRegression()
elif MODEL_TYPE == "Lasso":
    model = Lasso(alpha=ALPHA)
elif MODEL_TYPE == "Ridge":
    model = Ridge(alpha=ALPHA)
else:
    raise ValueError("Unknown model type")

model.fit(X_train_scaled, y_train)

# ---------------------------------------------------------
# 4. Evaluation
# ---------------------------------------------------------
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model: {MODEL_TYPE}")
print(f"MSE: {mse:.4f}")
print(f"R2: {r2:.4f}")

# ---------------------------------------------------------
# 5. Save Artifacts (Model & Metrics)
# ---------------------------------------------------------
# Create the models directory if it doesn't exist
os.makedirs(models_dir, exist_ok=True)

# Save Model
model_path = os.path.join(models_dir, 'model.pkl')
joblib.dump(model, model_path)

# Save Metrics to JSON
metrics = {
    "model_type": MODEL_TYPE,
    "mse": mse,
    "r2_score": r2,
    "hyperparameters": {
        "test_size": TEST_SIZE,
        "alpha": ALPHA if MODEL_TYPE in ["Lasso", "Ridge"] else "N/A"
    }
}

metrics_path = os.path.join(models_dir, 'metrics.json')
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=4)

# ---------------------------------------------------------
# 6. Generate GitHub Step Summary
# ---------------------------------------------------------
summary_content = f"""
# 🍷 Wine Quality Prediction Experiment

**Student:** {STUDENT_NAME} ({ROLL_NUMBER})

## 📊 Experiment Results
| Metric | Value |
| :--- | :--- |
| **Model Type** | {MODEL_TYPE} |
| **MSE** | {mse:.4f} |
| **R² Score** | {r2:.4f} |

## ⚙️ Configuration
- **Test Split:** {TEST_SIZE}
- **Alpha:** {ALPHA}
"""

report_path = os.path.join(models_dir, 'summary_report.md')
with open(report_path, 'w') as f:
    f.write(summary_content)

print("Training completed and artifacts saved.")