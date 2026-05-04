def generate_reason(severity, previous_use, duration, infection, setting, risk):
    reasons = []

    if severity == 2:
        reasons.append("high severity")

    if previous_use == 1:
        reasons.append("previous antibiotic use")

    if duration > 7:
        reasons.append("long duration")

    if infection == 1:
        reasons.append("respiratory infection")

    if setting == 1:
        reasons.append("hospital case")

    reasons.append(str(risk).lower() + " resistance")

    return "Selected due to " + ", ".join(reasons)


def get_confidence(prob):
    return round(prob * 100, 1)


def get_alert(prob):
    if prob > 0.7:
        return "HIGH"
    elif prob > 0.4:
        return "MEDIUM"
    else:
        return "LOW"