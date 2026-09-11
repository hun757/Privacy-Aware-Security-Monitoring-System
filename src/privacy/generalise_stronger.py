import pandas as pd

INPUT_PATH = "data/raw/synthetic_users.csv"
OUTPUT_PATH = "data/processed/generalised_stronger.csv"

def generalise_age(age):
    if age<30:
        return "18-29"
    elif age <50:
        return "30-49"
    else:
        return "50-65"

def generalise_postcode(postcode):
    postcode=str(postcode)
    return postcode[:2] + "**"

def generalise_income(income):
    lower = (income // 20000) * 20000
    upper = lower + 20000
    return str(lower // 1000) + "k-" + str(upper // 1000) + "k"


def generalise_occupation(occupation):
    if occupation in ["Data Analyst", "Software Engineer", "Cyber Security Analyst"]:
        return "Technology"
    elif occupation in ["Accountant", "Financial Analyst"]:
        return "Finance"
    elif occupation == "Teacher":
        return "Education"
    elif occupation == "Nurse":
        return "Healthcare"
    elif occupation in ["Marketing Specialist", "Sales Representative"]:
        return "Business"
    elif occupation == "Project Manager":
        return "Management"

def main():
    df = pd.read_csv(INPUT_PATH)
    generalised_df = pd.DataFrame()

    generalised_df["record_id"] = df["record_id"]
    generalised_df["age_group"] = df["age"].apply(generalise_age)
    generalised_df["postcode_group"] = df["postcode"].apply(generalise_postcode)
    generalised_df["income_range"] = df["income"].apply(generalise_income)
    generalised_df["occupation_group"] = df["occupation"].apply(generalise_occupation)

    generalised_df.to_csv(OUTPUT_PATH, index=False)

    print(generalised_df.head())
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()