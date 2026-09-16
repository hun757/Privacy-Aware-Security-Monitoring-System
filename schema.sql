-- ============================================================
-- Security Monitoring & Privacy System
-- Database Schema: raw synthetic data vs. generalised (protected) data
-- ============================================================

-- 1) RAW synthetic data (output of generate_data.py, 5,000 rows)
--    Used only for experimentation / generalisation / privacy evaluation.
--    Must NEVER be queried directly by the API or any user-facing service.
CREATE TABLE SYNTHETIC_DATA (
    record_id   INTEGER PRIMARY KEY,
    age         INTEGER,
    postcode    VARCHAR(4),
    income      INTEGER,
    occupation  VARCHAR(50)
);

-- 2) Generalised / protected data (output of generalise.py)
--    This is the table the API actually serves to users.
--    record_id is a FK back to SYNTHETIC_DATA so the mapping between
--    raw and generalised records is enforced at the database level.
CREATE TABLE PROTECTED_DATA (
    record_id        INTEGER PRIMARY KEY
                      REFERENCES SYNTHETIC_DATA(record_id),
    age_group        VARCHAR(20),
    postcode_group   VARCHAR(20),
    income_range     VARCHAR(20),
    occupation_group VARCHAR(50)
);

-- ============================================================
-- TODO (still to be agreed with the team — does not block schema work)
--   1. If k-anonymity processing suppresses some records, PROTECTED_DATA
--      may end up with fewer than 5,000 rows -> decide on a policy.
--   2. Decide whether "only PROTECTED_DATA is served" should be enforced
--      at the DB permission level (e.g. the API's DB account has no
--      SELECT grant on SYNTHETIC_DATA at all).
-- ============================================================

-- ============================================================
-- Login & access logging (SCRUM-29, SCRUM-30)
-- Separate from the project's dataset tables above.
-- ============================================================

CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE access_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NULL,
    username    VARCHAR(50),
    action      VARCHAR(50) NOT NULL,
    ip_address  VARCHAR(45),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;


-- ============================================================
-- Security alerts (SCRUM-39)
-- Stores flagged suspicious (ip, minute-window) events from
-- extract_features.py: brute-force, high request rate, bulk access.
-- ============================================================

CREATE TABLE security_alerts (
    alert_id     INT AUTO_INCREMENT PRIMARY KEY,
    alert_type   VARCHAR(50) NOT NULL,
    ip_address   VARCHAR(45) NOT NULL,
    window_start DATETIME NOT NULL,
    details      VARCHAR(255),
    severity     VARCHAR(20) DEFAULT 'medium',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_alert (alert_type, ip_address, window_start)
) ENGINE=InnoDB;