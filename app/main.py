from flask import Flask, render_template, request
import os
import pandas as pd

from model import predict
from utils import generate_reason, get_alert

app = Flask(__name__)

infection_map = {"UTI": 0, "Respiratory": 1, "Blood": 2, "Skin": 3}
sample_map = {"Urine": 0, "Blood": 1, "Sputum": 2, "Wound": 3}
age_map = {"Child": 0, "Adult": 1, "Elderly": 2}

severity_map = {"Mild": 0, "Moderate": 1, "Severe": 2}
setting_map = {"Community": 0, "Hospital": 1}
prev_map = {"No": 0, "Yes": 1}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

antibiotic_path = os.path.join(BASE_DIR, "Data", "raw", "amr_data.csv")
antibiotics_df = pd.read_csv(antibiotic_path)

country_mapping = {
    "Canada": 10,
    "UK": 20,
    "USA": 30
}

antibiotic_mapping = {
    "Amoxicillin": 0,
    "Ciprofloxacin": 1,
    "Doxycycline": 2,
    "Azithromycin": 3,
    "Cephalexin": 4
}


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


@app.route("/", methods=["GET", "POST"])
def home():
    antibiotic_list = antibiotics_df["Name"].unique()
    result = None
    recommendations = None

    if request.method == "POST":
        year = int(request.form.get("year", 2020))
        country_name = request.form.get("country", "UK")

        severity = severity_map.get(request.form.get("severity", "Mild"))
        setting = setting_map.get(request.form.get("setting", "Community"))
        previous_use = prev_map.get(request.form.get("previous_use", "No"))

        infection = infection_map.get(request.form.get("infection", "UTI"))
        sample = sample_map.get(request.form.get("sample", "Urine"))
        age_group = age_map.get(request.form.get("age_group", "Adult"))

        duration = int(request.form.get("duration", 5))
        country = country_mapping.get(country_name, 20)

        results = []

        for ab in antibiotic_list:
            antibiotic_code = antibiotic_mapping.get(ab, 0)

            pred, prob = predict(
                year,
                country,
                antibiotic_code,
                severity,
                setting,
                previous_use,
                duration,
                infection,
                sample,
                age_group
            )

            risk = get_alert(prob)

            results.append({
                "antibiotic": ab,
                "probability": float(round(prob, 2)),
                "risk": risk,
                "prediction": pred
            })

        results = sorted(results, key=lambda x: x["probability"])
        recommendations = results[:5]
        best = recommendations[0]

        info = get_antibiotic_info(best["antibiotic"])

        reason_text = generate_reason(
            severity,
            previous_use,
            duration,
            infection,
            setting,
            best["risk"]
        )

        if best["risk"] == "HIGH":
            next_step = "High resistance risk. Consider alternative antibiotics and perform susceptibility testing."
            experiment_plan = "Perform MIC testing and explore alternative antibiotic classes."
        elif best["risk"] == "MEDIUM":
            next_step = "Moderate resistance risk. Monitor closely and validate with lab testing."
            experiment_plan = "Conduct susceptibility testing and monitor response."
        else:
            next_step = "Low resistance risk. Safe to proceed with standard treatment."
            experiment_plan = "Standard lab validation sufficient."

        result = {
            "prediction": f"Best Option: {best['antibiotic']}",
            "probability": best["probability"],
            "risk_level": best["risk"],
            "reason": reason_text,
            "extra_info": info,
            "next_step": next_step,
            "experiment_plan": experiment_plan,
            "disclaimer": "This tool is for decision support only and does not replace clinical judgment."
        }

    return render_template(
        "dashboard.html",
        result=result,
        antibiotics=antibiotic_list,
        recommendations=recommendations
    )


@app.route("/experiment-planner", methods=["GET", "POST"])
def experiment_planner():
    plan = None
    risk = request.form.get("risk", "MEDIUM")

    if request.method == "POST":
        exp_type = request.form.get("exp_type")
        level = request.form.get("level")

        if level == "Beginner":
            complexity = "LOW"
            safety_note = "Use basic lab safety and supervisor guidance."
        elif level == "Intermediate":
            complexity = "MEDIUM"
            safety_note = "Requires careful handling, sterile technique, and supervision."
        else:
            complexity = "HIGH"
            safety_note = "Advanced workflow. Requires strict protocol control and trained supervision."

        if exp_type == "AST":

            steps = [
                "Collect sample",
                "Culture bacteria",
                "Apply antibiotic discs",
                "Incubate under controlled conditions",
                "Measure inhibition zones"
            ]
            materials = "Petri dish, agar, antibiotic discs, incubator"
            outcome = "Clear zones indicate sensitivity"
            mistakes = "Wrong incubation time, contamination"

        elif exp_type == "PCR":
            steps = "1. Extract DNA\n2. Prepare PCR mix\n3. Run thermal cycles\n4. Analyze gel"
            materials = "PCR machine, primers, DNA sample"
            outcome = "DNA amplification bands"
            mistakes = "Incorrect primer design, contamination"

        else:
            steps = "1. Collect sample\n2. Inoculate media\n3. Incubate\n4. Observe growth"
            materials = "Culture media, incubator"
            outcome = "Visible bacterial colonies"
            mistakes = "Improper sterilization"

        plan = {
            "steps": steps,
            "materials": materials,
            "outcome": outcome,
            "mistakes": mistakes,
            "complexity": complexity,
            "safety_note": safety_note,
            "risk": risk,
        }

    return render_template("experiment_planner.html", plan=plan)


@app.route("/simulation-lab")
def simulation_lab():
    return render_template("simulation_lab.html")


@app.route("/ai-assistant")
def ai_assistant():
    return render_template("ai_assistant.html")


@app.route("/drug-discovery")
def drug_discovery():
    return render_template("drug_discovery.html")


if __name__ == "__main__":
    app.run(debug=True)