import pickle
import os
import numpy as np
import pandas as pd

# Load model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

def predict(year, country):
    # Prepare input
    input_data = pd.DataFrame([[year, country]], columns=["Year", "Country"])

    # Prediction
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    # Risk Level
    if probability > 0.7:
        risk = "HIGH"
    elif probability > 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Explanation (simple rule-based for now)
    if prediction == 1:
        reason = "Higher resistance likelihood based on historical patterns in this region and time."
    else:
        reason = "Lower resistance likelihood based on historical patterns in this region and time."


    # Output
    result = {
        "prediction": "Resistant" if prediction == 1 else "Not Resistant",
        "probability": float(round(probability, 2)),
        "risk_level": risk,
        "reason": reason,
        "disclaimer": "This tool is for decision support only and does not replace clinical judgment.",
    }

    return result


# Test run
if __name__ == "__main__":
    output = predict(2015, 10)
    print("\n--- Prediction Result ---")
    print(f"Prediction: {output['prediction']}")
    print(f"Probability: {output['probability']}")
    print(f"Risk Level: {output['risk_level']}")

    print("\nReason:")
    print(output["reason"])

    print("\n⚠️ Disclaimer:")
    print(output["disclaimer"])