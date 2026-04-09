import pandas as pd
import os
import random
# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load data
file_path = os.path.join(BASE_DIR, "Data", "raw", "amr_data.csv")

data = pd.read_csv(file_path)

print(data.head())
print(data.columns)
print(data.info())

file_path = os.path.join(BASE_DIR, "Data", "raw", "metadata.csv")
data = pd.read_csv(file_path)

# Keep only relevant columns
data = data[["Year", "Country", "Ciprofloxacin", "cip_sr"]]


# Drop missing values
data = data.dropna()

# Clean Ciprofloxacin column
data["Ciprofloxacin"] = data["Ciprofloxacin"].astype(str)

# Remove unwanted symbols
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace(">", "", regex=False)
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace("<", "", regex=False)
data["Ciprofloxacin"] = data["Ciprofloxacin"].str.replace("=", "", regex=False)

# Convert to numeric safely
data["Ciprofloxacin"] = pd.to_numeric(data["Ciprofloxacin"], errors="coerce")

# Drop rows that still couldn't convert
data = data.dropna()
# Convert to float
data["Ciprofloxacin"] = data["Ciprofloxacin"].astype(float)

# 🔥 FIX 2: Convert types
data["Year"] = data["Year"].astype(int)
data["cip_sr"] = data["cip_sr"].astype(int)

# 🔥 FIX 3: Encode Country
data["Country"] = data["Country"].astype("category").cat.codes
# Simulate multiple antibiotics (0 to 4)
# Create antibiotic categories
data["Antibiotic"] = [random.randint(0, 4) for _ in range(len(data))]

# 🔥 Create relationship with resistance
def adjust_resistance(row):
    # Example logic:
    # Antibiotic 0 → low resistance
    # Antibiotic 4 → high resistance

    if row["Antibiotic"] == 4:
        return 1 if random.random() > 0.3 else 0
    elif row["Antibiotic"] == 3:
        return 1 if random.random() > 0.5 else 0
    elif row["Antibiotic"] == 2:
        return row["cip_sr"]
    else:
        return 0 if random.random() > 0.7 else 1

data["cip_sr"] = data.apply(adjust_resistance, axis=1)
# Show result
print(data.head())
print(data.info())
output_path = os.path.join(BASE_DIR, "Data", "processed", "cleaned_data.csv")

# Create folder if not exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save file
data.to_csv(output_path, index=False)

print("✅ Data saved to:", output_path)