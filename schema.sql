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
