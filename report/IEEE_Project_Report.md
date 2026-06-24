# IEEE Project Report

## Title
Encrypted Database Management System Using MySQL

## Abstract
This project presents a secure web-based database management system that protects sensitive customer information by encrypting data before storage in MySQL and decrypting it only for authenticated and authorized users. The system combines Flask, SQLAlchemy, bcrypt password hashing, AES-256 encryption using the Cryptography library, session authentication, and role-based access control. The result is a practical encrypted data management platform with auditing, failed login tracking, and security dashboard analytics.

## 1. Introduction
Traditional database systems often store sensitive data in plaintext or rely on access control alone. That approach does not protect data at rest if the database is compromised. This project addresses that limitation by adding application-level encryption with AES-256, so protected fields are unreadable inside the database.

## 2. Problem Statement
A customer database can expose names, emails, phone numbers, and addresses if access controls fail or if the database files are stolen. A secure system must protect both authentication credentials and stored customer data while still allowing authorized users to perform business operations.

## 3. Objectives
- Encrypt sensitive customer attributes before MySQL storage.
- Hash user passwords using bcrypt.
- Use Flask sessions for secure authentication.
- Enforce role-based access control for Admin, Manager, and Employee roles.
- Maintain an audit trail for security-sensitive operations.
- Detect and store failed login attempts.
- Provide a dashboard for security monitoring.

## 4. Technologies Used
- Frontend: HTML, CSS, Bootstrap 5
- Backend: Python Flask
- ORM: SQLAlchemy
- Database: MySQL with mysql-connector-python
- Encryption: AES-256 with the Cryptography library
- Authentication: Flask sessions and bcrypt password hashing

## 5. System Design
### 5.1 Architecture
The architecture follows a three-layer model:
- Presentation layer: Bootstrap-based web pages
- Application layer: Flask routes, authentication, encryption, and audit logic
- Data layer: MySQL database tables, procedures, triggers, and views

### 5.2 Data Flow
1. A user registers or logs in.
2. Flask hashes the password with bcrypt.
3. After authentication, a session is created.
4. Customer data entered by the user is encrypted with AES-256.
5. Encrypted values are stored in MySQL.
6. Authorized users request records.
7. The application decrypts data only after role verification.
8. Every important event is written to audit logs.

## 6. Database Design
The schema contains four core tables:
- users: stores account credentials and roles.
- customer_data: stores encrypted customer fields.
- audit_logs: stores application and trigger-based events.
- failed_logins: stores suspicious authentication attempts.

### 6.1 Key Security Design Choice
The project uses AES-GCM with a 256-bit key. The database stores only ciphertext, while the encryption key stays in application configuration.

### 6.2 Indexing Strategy
Indexes are added to support:
- user lookups by username and email
- audit log filtering by user and time
- failed login analysis by username and time
- customer records by creator and creation time

## 7. Functional Modules
### 7.1 User Authentication Module
- Registration with bcrypt password hashing
- Session-based login and logout
- Login failure tracking

### 7.2 Role-Based Access Control
- Admin: full access, user management, audit logs
- Manager: customer management and audit review
- Employee: limited customer access and dashboard access

### 7.3 Customer Data Management
- Add, view, edit, delete, and search customer records
- Fields encrypted before persistence
- Decryption only for authenticated users

### 7.4 Audit Trail Module
- Login and logout events
- Customer insert, update, and delete actions
- Decryption request tracking
- User role updates
- Dashboard access tracking

### 7.5 Security Dashboard
- Total users
- Total encrypted customer records
- Recent activities
- Security alerts
- Failed login attempts

## 8. Stored Procedures, Triggers, and Views
### Stored Procedures
- sp_register_user
- sp_add_customer
- sp_update_customer
- sp_delete_customer
- sp_log_audit

### Triggers
- AFTER INSERT trigger for customer_data
- AFTER UPDATE trigger for customer_data
- AFTER DELETE trigger for customer_data

### Views
- vw_customer_records
- vw_audit_trail
- vw_security_overview

## 9. Backup and Recovery
Logical backup is implemented with MySQL utilities such as mysqldump. The recovery process restores the dump file back into the encrypted_dbms database. Regular backup validation is recommended.

## 10. Testing Strategy
The system should be validated by checking:
- successful registration and login
- failed login tracking
- encrypted values stored in the database
- authorized decryption behavior
- role-based access denial for unauthorized users
- audit entries created for key actions

## 11. Conclusion
This project demonstrates how Flask, MySQL, AES-256, bcrypt, and auditing can be combined to create a secure encrypted database management system. It improves data confidentiality at rest while preserving controlled access for operational workflows.

## 12. Future Scope
- Column-level searchable encryption
- Two-factor authentication
- File upload encryption
- Data export controls
- REST API version of the same system

## References
- Flask Documentation
- SQLAlchemy Documentation
- Cryptography Library Documentation
- MySQL Reference Manual
