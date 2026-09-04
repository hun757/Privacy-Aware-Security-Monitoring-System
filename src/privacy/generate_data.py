import random
import pandas as pd

"""
generate_data.py

Generate synthetic personal-style data for the Privacy-Aware Security Monitoring System.
The generated dataset does not contain real personal information.
"""

NUM_RECORDS = 5000
RANDOM_SEED = 42
OUTPUT_PATH = "data/raw/synthetic_users.csv"

INCOME_RANGES = {
    "Data Analyst": (65000, 110000),
    "Software Engineer": (75000, 140000),
    "Cyber Security Analyst": (80000, 145000),
    "Accountant": (60000, 110000),
    "Financial Analyst": (65000, 120000),
    "Teacher": (65000, 115000),
    "Nurse": (70000, 120000),
    "Marketing Specialist": (60000, 110000),
    "Project Manager": (80000, 140000),
    "Sales Representative": (55000, 110000),
}

POSTCODES = [
    "2000", "2007", "2010", "2015", "2020", "2031",
    "2042", "2050", "2060", "2077", "2095", "2112",
    "2122", "2134", "2145", "2150", "2155", "2160",
    "2170", "2190", "2200", "2217", "2220", "2230",
]

# Generate income using occupation-specific ranges and a weak age effect
def generate_income(age, occupation):
    min_income, max_income = INCOME_RANGES[occupation]

    # Scale age to 0-1 so older records trend toward the upper salary range
    age_factor = (age-18) / (65-18)
    
    expected_income = min_income + (
        (max_income - min_income) * age_factor
    )

    # Add noise so age does not directly determine income
    income = expected_income + random.randint(-10000,10000)

    return round(max(min_income, min(income, max_income)))


# Generate one synthetic record
def generate_record(record_id):
    age = random.randint(18,65)
    occupation = random.choice(list(INCOME_RANGES))
    postcode = random.choice(POSTCODES)
    income = generate_income(age, occupation)

    return {
        "record_id": record_id,
        "age": age,
        "postcode": postcode,
        "income": income,
        "occupation": occupation,
    }


# Generate a synthetic dataset
def generate_dataset(num_records):
    records = [
        generate_record(record_id)
        for record_id in range(1, num_records+1)
    ]

    return pd.DataFrame(records)

# Validate basic dataset quality requirements
def validate_dataset(df):
    """Validate the generated synthetic dataset."""

    valid = True

    if len(df) != NUM_RECORDS:
        valid = False

    if df.isnull().sum().sum() != 0:
        valid = False

    if df["record_id"].duplicated().sum() != 0:
        valid = False

    invalid_ages = df[
        (df["age"] < 18) | (df["age"] > 65)
    ]

    if len(invalid_ages) != 0:
        valid = False

    invalid_incomes = df[df["income"] <= 0]

    if len(invalid_incomes) != 0:
        valid = False

    return valid

# Save the dataset as CSV
def save_dataset(df, output_path):
    df.to_csv(output_path, index=False)

def main():
    random.seed(RANDOM_SEED)

    dataset = generate_dataset(NUM_RECORDS)

    is_valid = validate_dataset(dataset)

    if is_valid:
        save_dataset(dataset, OUTPUT_PATH)
        print("Dataset generated and saved successfully.")
        print(dataset.head())
    else:
        print("Dataset validation failed.")

if __name__ == "__main__":
    main()
