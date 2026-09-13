"""
API server skeleton (SCRUM-19) + Login endpoint (SCRUM-29)
+ Access logging for every request (SCRUM-30, SCRUM-35).

Run with:
    python app.py

Then test with:
    curl -X POST http://localhost:5001/login \
         -H "Content-Type: application/json" \
         -d '{"username": "admin", "password": "your_password"}'
"""

import os
import time
import datetime

import jwt
from flask import Flask, request, jsonify, g
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

from db.db_connection import get_connection  # reuse the module from SCRUM-27

load_dotenv()

app = Flask(__name__)

# Used to sign login tokens. Set this in your .env file — never hardcode
# a real secret in code that goes to GitHub.
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-secret-change-me")
JWT_EXPIRY_HOURS = 4


@app.before_request
def _start_request_timer():
    """Record when the request came in, so we can calculate response_time_ms later."""
    g.request_start_time = time.perf_counter()


@app.after_request
def _log_every_request(response):
    """Log every request (login or not) into access_log automatically.

    Centralising this in one hook means any new API route added later
    gets logged automatically, without extra logging code in each route.
    """
    try:
        elapsed_ms = int(
            (time.perf_counter() - g.get("request_start_time", time.perf_counter())) * 1000
        )
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO access_log "
                "(user_id, username, action, method, path, status_code, response_time_ms, ip_address) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    g.get("log_user_id"),
                    g.get("log_username"),
                    g.get("log_action", f"{request.method} {request.path}"),
                    request.method,
                    request.path,
                    response.status_code,
                    elapsed_ms,
                    request.remote_addr,
                ),
            )
            conn.commit()
            cursor.close()
    except Exception as e:
        # A logging failure should never block the actual API response.
        app.logger.warning(f"access_log insert failed: {e}")
    return response


@app.route("/", methods=["GET"])
def health_check():
    """Basic route so you can confirm the server is running at all."""
    return jsonify({"status": "ok", "service": "Security Monitoring & Privacy System API"})


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
        g.log_username = username
        g.log_action = "login_failed"
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

    g.log_user_id = user["user_id"]
    g.log_username = user["username"]
    g.log_action = "login_success"

    return jsonify({"token": token, "expires_in_hours": JWT_EXPIRY_HOURS})


if __name__ == "__main__":
    app.run(debug=True, port=5001)