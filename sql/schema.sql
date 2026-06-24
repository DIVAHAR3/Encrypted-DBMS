CREATE DATABASE IF NOT EXISTS encrypted_dbms
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE encrypted_dbms;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'MANAGER', 'EMPLOYEE') NOT NULL DEFAULT 'EMPLOYEE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS customer_data (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    encrypted_name TEXT NOT NULL,
    encrypted_email TEXT NOT NULL,
    encrypted_phone TEXT NOT NULL,
    encrypted_address TEXT NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS failed_logins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    attempt_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_customer_created_by ON customer_data(created_by);
CREATE INDEX idx_customer_created_at ON customer_data(created_at);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, log_time);
CREATE INDEX idx_audit_action_time ON audit_logs(action, log_time);
CREATE INDEX idx_failed_username_time ON failed_logins(username, attempt_time);

DELIMITER $$

CREATE PROCEDURE sp_register_user(
    IN p_username VARCHAR(100),
    IN p_email VARCHAR(150),
    IN p_password_hash VARCHAR(255),
    IN p_role VARCHAR(20)
)
BEGIN
    INSERT INTO users (username, email, password_hash, role)
    VALUES (p_username, p_email, p_password_hash, p_role);
END$$

CREATE PROCEDURE sp_add_customer(
    IN p_name TEXT,
    IN p_email TEXT,
    IN p_phone TEXT,
    IN p_address TEXT,
    IN p_created_by INT
)
BEGIN
    INSERT INTO customer_data (encrypted_name, encrypted_email, encrypted_phone, encrypted_address, created_by)
    VALUES (p_name, p_email, p_phone, p_address, p_created_by);
END$$

CREATE PROCEDURE sp_update_customer(
    IN p_customer_id INT,
    IN p_name TEXT,
    IN p_email TEXT,
    IN p_phone TEXT,
    IN p_address TEXT
)
BEGIN
    UPDATE customer_data
    SET encrypted_name = p_name,
        encrypted_email = p_email,
        encrypted_phone = p_phone,
        encrypted_address = p_address
    WHERE customer_id = p_customer_id;
END$$

CREATE PROCEDURE sp_delete_customer(IN p_customer_id INT)
BEGIN
    DELETE FROM customer_data WHERE customer_id = p_customer_id;
END$$

CREATE PROCEDURE sp_log_audit(
    IN p_user_id INT,
    IN p_action VARCHAR(100),
    IN p_description TEXT
)
BEGIN
    INSERT INTO audit_logs (user_id, action, description)
    VALUES (p_user_id, p_action, p_description);
END$$

CREATE OR REPLACE VIEW vw_customer_records AS
SELECT
    c.customer_id,
    c.encrypted_name,
    c.encrypted_email,
    c.encrypted_phone,
    c.encrypted_address,
    c.created_at,
    c.created_by,
    u.username AS creator_username,
    u.role AS creator_role
FROM customer_data c
JOIN users u ON u.user_id = c.created_by;

CREATE OR REPLACE VIEW vw_audit_trail AS
SELECT
    a.log_id,
    a.user_id,
    u.username,
    a.action,
    a.description,
    a.log_time
FROM audit_logs a
LEFT JOIN users u ON u.user_id = a.user_id;

CREATE OR REPLACE VIEW vw_security_overview AS
SELECT
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM customer_data) AS total_customers,
    (SELECT COUNT(*) FROM audit_logs) AS total_audit_logs,
    (SELECT COUNT(*) FROM failed_logins) AS total_failed_logins;

CREATE TRIGGER trg_customer_insert_audit
AFTER INSERT ON customer_data
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, description, log_time)
    VALUES (
        COALESCE(@app_user_id, NEW.created_by),
        'INSERT_CUSTOMER',
        CONCAT('Inserted customer record #', NEW.customer_id),
        CURRENT_TIMESTAMP
    );
END$$

CREATE TRIGGER trg_customer_update_audit
AFTER UPDATE ON customer_data
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, description, log_time)
    VALUES (
        COALESCE(@app_user_id, NEW.created_by),
        'UPDATE_CUSTOMER',
        CONCAT('Updated customer record #', NEW.customer_id),
        CURRENT_TIMESTAMP
    );
END$$

CREATE TRIGGER trg_customer_delete_audit
AFTER DELETE ON customer_data
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, description, log_time)
    VALUES (
        COALESCE(@app_user_id, OLD.created_by),
        'DELETE_CUSTOMER',
        CONCAT('Deleted customer record #', OLD.customer_id),
        CURRENT_TIMESTAMP
    );
END$$

DELIMITER ;

-- Backup and recovery notes:
-- Use mysqldump -u root -p encrypted_dbms > encrypted_dbms_backup.sql
-- Restore using mysql -u root -p encrypted_dbms < encrypted_dbms_backup.sql
