import pickle
import os
import pandas as pd

# Load model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)


# 🔥 UPGRADE 1 — Smart Reason Generator
def generate_reason(prob, infection, previous_use, age_group):
    if prob > 0.7:
        base = "High resistance risk"
    elif prob > 0.4:
        base = "Moderate resistance risk"
    else:
        base = "Low resistance risk"

    # Infection context
    if infection == 0:
        base += " commonly associated with urinary tract infections"
    elif infection == 1:
        base += " linked to respiratory infection patterns"
    elif infection == 2:
        base += " observed in bloodstream infections"
    elif infection == 3:
        base += " related to skin and soft tissue infections"

    # Patient factor
    if age_group == 2:
        base += " in elderly patients"

    # Antibiotic exposure
    if previous_use == 1:
        base += " with prior antibiotic exposure"

    return base


def predict(year, country,
            antibiotic=0,
            severity=0,
            setting=0,
            previous_use=0,
            duration=5,
            infection=0,
            sample=0,
            age_group=1):

    # ✅ CREATE INPUT DATA
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

    # ✅ Prediction
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    # ✅ Risk Level
    if probability > 0.7:
        risk = "HIGH"
    elif probability > 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # 🔥 UPGRADE 1 USED HERE
    reason = generate_reason(probability, infection, previous_use, age_group)

    # 🔥 UPGRADE 2 — Confidence Score
    confidence_score = abs(probability - 0.5) * 2

    if confidence_score > 0.6:
        confidence = "HIGH"
    elif confidence_score > 0.3:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # 🔥 UPGRADE 3 — Clinical Alert
    if probability > 0.75:
        alert = "⚠️ Avoid this antibiotic unless no alternatives are available"
    elif probability > 0.5:
        alert = "⚠️ Use with caution and confirm with lab testing"
    else:
        alert = "Suitable option under monitored conditions"

    # ✅ Output
    result = {
        "prediction": "Resistant" if prediction == 1 else "Not Resistant",
        "probability": float(round(probability, 2)),
        "risk_level": risk,
        "confidence": confidence,   # NEW
        "reason": reason,
        "alert": alert,             # NEW
        "disclaimer": "This tool is for decision support only and does not replace clinical judgment.",
    }

    return result


# ✅ Test run
if __name__ == "__main__":
    output = predict(2015, 10)

    print("\n--- Prediction Result ---")
    print(f"Prediction: {output['prediction']}")
    print(f"Probability: {output['probability']}")
    print(f"Risk Level: {output['risk_level']}")
    print(f"Confidence: {output['confidence']}")

    print("\nReason:")
    print(output["reason"])

    print("\nClinical Alert:")
    print(output["alert"])

    print("\n⚠️ Disclaimer:")
    print(output["disclaimer"])