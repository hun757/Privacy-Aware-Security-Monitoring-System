"""
API server skeleton (SCRUM-19) + Login endpoint (SCRUM-29).

Run with:
    python app.py

Then test with:
    curl -X POST http://localhost:5000/login \
         -H "Content-Type: application/json" \
         -d '{"username": "admin", "password": "your_password"}'
"""

import os
import datetime

import jwt
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

from db.db_connection import get_connection  # reuse the module from SCRUM-27

load_dotenv()

app = Flask(__name__)

# Used to sign login tokens. Set this in your .env file — never hardcode
# a real secret in code that goes to GitHub.
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-secret-change-me")
JWT_EXPIRY_HOURS = 4


@app.route("/", methods=["GET"])
def health_check():
    """Basic route so you can confirm the server is running at all."""
    return jsonify({"status": "ok", "service": "Security Monitoring & Privacy System API"})

def log_access(user_id, username, action):
    """로그인 시도 기록을 access_log 테이블에 남긴다 (누가/언제/성공인지)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO access_log (user_id, username, action, ip_address) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, username, action, request.remote_addr),
        )
        conn.commit()
        cursor.close()
        
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()

    if not user or not check_password_hash(user["password_hash"], password):
        # Same error for "no such user" and "wrong password" — don't leak
        # which one it was, that's a basic security hygiene practice.
        log_access(None, username, "login_failed")
        return jsonify({"error": "invalid username or password"}), 401

    token = jwt.encode(
        {
            "user_id": user["user_id"],
            "username": user["username"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    log_access(user["user_id"], user["username"], "login_success")

    return jsonify({"token": token, "expires_in_hours": JWT_EXPIRY_HOURS})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
