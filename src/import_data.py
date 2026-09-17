import csv
from pathlib import Path

from db.db_connection import get_connection


ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = ROOT / "data" / "raw" / "synthetic_users.csv"
PROTECTED_FILE = ROOT / "data" / "processed" / "generalised_users.csv"


def load_raw_data(cursor):
    with open(RAW_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                int(row["record_id"]),
                int(row["age"]),
                row["postcode"],
                int(row["income"]),
                row["occupation"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO SYNTHETIC_DATA
        (record_id, age, postcode, income, occupation)
        VALUES (%s, %s, %s, %s, %s)
        """,
        rows,
    )

    print(f"Inserted {len(rows)} rows into SYNTHETIC_DATA.")


def load_protected_data(cursor):
    with open(PROTECTED_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                int(row["record_id"]),
                row["age_group"],
                row["postcode_group"],
                row["income_range"],
                row["occupation_group"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO PROTECTED_DATA
        (record_id, age_group, postcode_group, income_range, occupation_group)
        VALUES (%s, %s, %s, %s, %s)
        """,
        rows,
    )

    print(f"Inserted {len(rows)} rows into PROTECTED_DATA.")


def main():
    with get_connection() as conn:
        cursor = conn.cursor()

        try:
            load_raw_data(cursor)
            load_protected_data(cursor)

            conn.commit()
            print("Import completed successfully.")

        except Exception:
            conn.rollback()
            print("Import failed. Changes rolled back.")
            raise

        finally:
            cursor.close()


if __name__ == "__main__":
    main()
