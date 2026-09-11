import pandas as pd

"""
analyse_privacy.py
Analyse record uniqueness in the generalised synthetic dataset.
"""

INPUT_PATH = "data/processed/generalised_users.csv"

QI_COLUMNS = [
    "age_group",
    "postcode_group",
    "income_range",
    "occupation_group"
]


def calculate_uniqueness(df):
    group_counts = df.groupby(QI_COLUMNS).size()

    unique_groups = group_counts[group_counts == 1]

    total_records = len(df)
    unique_records = len(unique_groups)
    uniqueness_rate = (unique_records / total_records) * 100
    smallest_group = group_counts.min()

    print("Total records: ", total_records)
    print("Unique records: ", unique_records)
    print("Uniqueness rate: ", round(uniqueness_rate, 2), "%")
    print("Smallest group size: ", smallest_group)


def main():
    dataset = pd.read_csv(INPUT_PATH)
    calculate_uniqueness(dataset)


if __name__ == "__main__":
    main()