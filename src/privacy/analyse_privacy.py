import pandas as pd

"""
analyse_privacy.py
Analyse record uniqueness in the generalised synthetic dataset.
"""

CURRENT_PATH = "data/processed/generalised_users.csv"
STRONGER_PATH = "data/processed/generalised_stronger.csv"

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


def evaluate_group_sizes(df):
    group_counts = df.groupby(QI_COLUMNS).size()

    size_1 = group_counts[group_counts == 1].sum()
    size_2 = group_counts[group_counts == 2].sum()
    size_3 = group_counts[group_counts == 3].sum()
    size_4 = group_counts[group_counts == 4].sum()
    size_5_plus = group_counts[group_counts >= 5].sum()

    print("\nGroup Size Analysis")
    print("Group size 1: ", size_1)
    print("Group size 2: ", size_2)
    print("Group size 3: ", size_3)
    print("Group size 4: ", size_4)
    print("Group size 5+: ", size_5_plus)

def evaluate_utility(current_df, stronger_df):
    columns = [
        "age_group",
        "postcode_group",
        "income_range",
        "occupation_group"
    ]

    print("\nDATA UTILITY")

    for column in columns:
        current_count = current_df[column].nunique()
        stronger_count = stronger_df[column].nunique()

        print(column)
        print("Current categories: ", current_count)
        print("Stronger categories: ", stronger_count)
        print()

def main():
    current_df = pd.read_csv(CURRENT_PATH)
    stronger_df = pd.read_csv(STRONGER_PATH)

    print("Current first row:")
    print(current_df.head(1))

    print("\nStronger first row:")
    print(stronger_df.head(1))

    print("\nCURRENT GENERALISATION")
    calculate_uniqueness(current_df)
    evaluate_group_sizes(current_df)

    print("\nSTRONGER GENERALISATION")
    calculate_uniqueness(stronger_df)
    evaluate_group_sizes(stronger_df)

    evaluate_utility(current_df, stronger_df)


if __name__ == "__main__":
    main()