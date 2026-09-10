"""
One-off script to create a test login account in the users table,
so you have something to log in with while testing /login.

Run with:
    python create_test_user.py
"""

from werkzeug.security import generate_password_hash
from db.db_connection import get_connection

TEST_USERNAME = "admin"
TEST_PASSWORD = "changeme123"  # change this, this is just for local testing


def main():
    password_hash = generate_password_hash(TEST_PASSWORD)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (TEST_USERNAME, password_hash),
        )
        conn.commit()
        cursor.close()

    print(f"Created user '{TEST_USERNAME}' with password '{TEST_PASSWORD}'.")
    print("Use these to test the /login endpoint, then delete this account before demoing.")


if __name__ == "__main__":
    main()
