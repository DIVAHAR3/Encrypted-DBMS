USE encrypted_dbms;

-- Register a user manually
INSERT INTO users (username, email, password_hash, role)
VALUES (?, ?, ?, ?);

-- Login lookup
SELECT user_id, username, email, password_hash, role
FROM users
WHERE username = ? OR email = ?
LIMIT 1;

-- Dashboard totals
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_customers FROM customer_data;
SELECT COUNT(*) AS total_failed_logins FROM failed_logins;
SELECT COUNT(*) AS total_audit_logs FROM audit_logs;

-- Customer list for the current user context
SELECT *
FROM vw_customer_records
WHERE created_by = ?
ORDER BY created_at DESC;

-- Customer list for privileged users
SELECT *
FROM vw_customer_records
ORDER BY created_at DESC;

-- Search customer records by decrypted values in the application layer.
-- The application decrypts rows after loading them because AES-GCM encryption is randomized.
SELECT * FROM vw_customer_records ORDER BY created_at DESC;

-- Audit log drill-down
SELECT * FROM vw_audit_trail ORDER BY log_time DESC LIMIT 200;

-- Failed login review
SELECT * FROM failed_logins ORDER BY attempt_time DESC LIMIT 50;

-- Add encrypted customer payload via stored procedure
SET @app_user_id := ?;
CALL sp_add_customer(?, ?, ?, ?, ?);

-- Update encrypted customer payload via stored procedure
SET @app_user_id := ?;
CALL sp_update_customer(?, ?, ?, ?, ?);

-- Delete customer via stored procedure
SET @app_user_id := ?;
CALL sp_delete_customer(?);
