import pickle
import os
import pandas as pd

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "model.pkl")

# Load model ONCE
with open(model_path, "rb") as f:
    model = pickle.load(f)


def predict(year, country,
            antibiotic=0,
            severity=0,
            setting=0,
            previous_use=0,
            duration=5,
            infection=0,
            sample=0,
            age_group=1):

    input_data = pd.DataFrame([[
        year,
        country,
        antibiotic,
        severity,
        setting,
        previous_use,
        duration,
        infection,
        sample,
        age_group
    ]], columns=[
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
    ])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    return prediction, probability