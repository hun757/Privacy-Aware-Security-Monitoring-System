import pandas as pd
"""
generalise.py
Generalise quasi-identifiers in the synthetic dataset for the Privacy-Aware Security Monitoring System.
"""

INPUT_PATH = "data/raw/synthetic_users.csv"
OUTPUT_PATH = "data/processed/generalised_users.csv"

# Generalise age into age groups
def generalise_age(age):
    if age<20:
        return "18-19"
    elif age<30:
        return "20-29"
    elif age<40:
        return "30-39"
    elif age<50:
        return "40-49"
    elif age<60:
        return "50-59"
    else :
        return "60-65"

# Generalise postcode by keeping the first two digits
def generalise_postcode(postcode):
    postcode=str(postcode)
    return postcode[:2] + "**"

# Generalise income into $10,000 ranges
def generalise_income(income):
    lower = (income//10000) * 10000
    upper = lower + 10000
    return str(lower//1000)+"k-" + str(upper//1000)+"k"

# Generalise occupation into categories
def generalise_occupation(occupation):
    if occupation in ["Data Analyst", "Software Engineer", "Cyber Security Analyst"]:
        return "Technology"
    elif occupation in ["Accountant", "Financial Analyst"]:
        return "Finance"
    elif occupation == "Teacher":
        return "Education"
    elif occupation == "Nurse":
        return "Medical"
    elif occupation in ["Marketing Specialist", "Sales Representative"]:
        return "Business"
    elif occupation == "Project Manager":
        return "Management"

# Apply generalisation rules to the dataset
def generalise_dataset(df):
    generalised_df = pd.DataFrame()

    generalised_df['record_id'] = df['record_id']
    generalised_df['age_group'] = df['age'].apply(generalise_age)
    generalised_df["postcode_group"] = df["postcode"].apply(generalise_postcode)
    generalised_df["income_range"] = df["income"].apply(generalise_income)
    generalised_df["occupation_group"] = df["occupation"].apply(generalise_occupation)

    return generalised_df


# Validate the generalised dataset
def validate_dataset(df):
    valid = True

    print("Number of records:", len(df))
    print("Missing values by column:")
    print(df.isnull().sum())
    print("Duplicate record IDs:", df["record_id"].duplicated().sum())

    if len(df) != 5000:
        valid = False
    if df.isnull().sum().sum() != 0:
        valid = False
    if df['record_id'].duplicated().sum() != 0:
        valid = False
    return valid

# Save generalised dataset
def save_dataset(df, output_path):
    df.to_csv(output_path, index=False)


def main():
    dataset=pd.read_csv(INPUT_PATH)
    print(dataset["occupation"].value_counts())
    generalised_dataset = generalise_dataset(dataset)
    is_valid = validate_dataset(generalised_dataset)

    if is_valid:
        save_dataset(generalised_dataset, OUTPUT_PATH)
        print("Dataset generalised and saved successfully.")
        print(generalised_dataset.head())
    else:
        print("Generalised dataset validation failed.")


if __name__ == "__main__":
    main()