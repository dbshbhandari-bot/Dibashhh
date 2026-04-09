from flask import Flask, render_template, request
import pickle
import os
import pandas as pd

app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load antibiotic dataset
antibiotic_path = os.path.join(BASE_DIR, "Data", "raw", "amr_data.csv")
antibiotics_df = pd.read_csv(antibiotic_path)

# Country mapping
country_mapping = {
    "Canada": 10,
    "UK": 20,
    "USA": 30
}

# ✅ FIX 1: Proper antibiotic mapping (NOT hash)
antibiotic_mapping = {
    "Amoxicillin": 0,
    "Ciprofloxacin": 1,
    "Doxycycline": 2,
    "Azithromycin": 3,
    "Cephalexin": 4
}

# Load model
model_path = os.path.join(BASE_DIR, "models", "model.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)


# Get antibiotic info
def get_antibiotic_info(name):
    row = antibiotics_df[antibiotics_df["Name"] == name]

    if not row.empty:
        return {
            "family": row.iloc[0]["Family"],
            "usage": row.iloc[0]["Usage"]
        }
    return {
        "family": "Unknown",
        "usage": "No data available"
    }


# Prediction function
def predict(year, country, antibiotic):
    input_data = pd.DataFrame(
        [[year, country, antibiotic]],
        columns=["Year", "Country", "Antibiotic"]
    )

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    return prediction, probability


@app.route("/", methods=["GET", "POST"])
def home():
    antibiotic_list = antibiotics_df["Name"].unique()
    result = None
    recommendations = None

    if request.method == "POST":
        year = int(request.form["year"])
        country_name = request.form["country"]
        antibiotic_name = request.form["antibiotic"]
        infection = request.form["infection"]
        sample = request.form["sample"]
        age_group = request.form["age_group"]

        country = country_mapping[country_name]

        results = []

        # 🔥 LOOP THROUGH ALL ANTIBIOTICS
        for ab in antibiotic_list:

            # ✅ FIX 2: Use real mapping instead of hash
            antibiotic_code = antibiotic_mapping.get(ab, 0)

            pred, prob = predict(year, country, antibiotic_code)

            # Risk level
            if prob > 0.7:
                risk = "HIGH"
            elif prob > 0.4:
                risk = "MEDIUM"
            else:
                risk = "LOW"

            results.append({
                "antibiotic": ab,
                "probability": float(round(prob, 2)),
                "risk": risk,
                "prediction": pred
            })

        # Sort by lowest resistance
        results = sorted(results, key=lambda x: x["probability"])

        recommendations = results[:5]
        best = recommendations[0]

        # Get info
        info = get_antibiotic_info(best["antibiotic"])

        # ✅ FIX 3: Use best prediction (not wrong variable)
        if best["prediction"] == 1:
            next_step = "High resistance risk. Consider alternative antibiotics and perform susceptibility testing."
        else:
            next_step = "Low resistance risk. Monitor patient and continue current antibiotic."

        # Experimental planner
        if best["probability"] > 0.6:
            experiment_plan = "Test alternative antibiotic classes and perform MIC testing."
        else:
            experiment_plan = "Standard susceptibility testing recommended."

        # Final result
        result = {
            "prediction": f"Best Option: {best['antibiotic']}",
            "probability": best["probability"],
            "risk_level": best["risk"],
            "reason": "Recommended based on lowest predicted resistance risk.",
            "extra_info": info,
            "next_step": next_step,
            "experiment_plan": experiment_plan,
            "disclaimer": "This tool is for decision support only and does not replace clinical judgment."
        }

    return render_template(
        "index.html",
        result=result,
        antibiotics=antibiotic_list,
        recommendations=recommendations
    )


if __name__ == "__main__":
    app.run(debug=True)
