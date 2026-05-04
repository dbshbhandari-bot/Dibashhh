import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load dataset
file_path = os.path.join(BASE_DIR, "Data", "processed", "cleaned_data.csv")
data = pd.read_csv(file_path)

# Keep relevant columns
data = data[["Year", "Country", "Ciprofloxacin", "cip_sr","Antibiotic",
    "Severity",
    "Setting",
    "Previous_Use",
    "Duration",
    "Infection",
    "Sample",
    "Age_Group"
]]
data = data.dropna()

# Clean Ciprofloxacin
data["Ciprofloxacin"] = data["Ciprofloxacin"].astype(str)
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace(">", "", regex=False)
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace("<", "", regex=False)
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace("=", "", regex=False)
data["Ciprofloxacin"] = pd.to_numeric(data["Ciprofloxacin"], errors="coerce")
data = data.dropna()

# Convert types
data["Year"] = data["Year"].astype(int)
data["cip_sr"] = data["cip_sr"].astype(int)
data["Country"] = data["Country"].astype("category").cat.codes

# Features and target
X = data[[
    "Year",
    "Country",
    "Antibiotic",
    "Severity",
    "Setting",
    "Previous_Use",
    "Duration",
    "Infection",
    "Sample",
    "Age_Group"
]]
y = data["cip_sr"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Accuracy
from sklearn.metrics import classification_report, confusion_matrix

y_pred = model.predict(X_test)

print(f"Model Accuracy: {model.score(X_test, y_test):.2f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
model_path = os.path.join(BASE_DIR, "models", "model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully!")