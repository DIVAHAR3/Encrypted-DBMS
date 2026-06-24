# Diagrams

## ER Diagram

```mermaid
erDiagram
    USERS ||--o{ CUSTOMER_DATA : creates
    USERS ||--o{ AUDIT_LOGS : records
    USERS ||--o{ FAILED_LOGINS : generates

    USERS {
        int user_id PK
        string username
        string email
        string password_hash
        enum role
        datetime created_at
    }

    CUSTOMER_DATA {
        int customer_id PK
        text encrypted_name
        text encrypted_email
        text encrypted_phone
        text encrypted_address
        int created_by FK
        datetime created_at
    }

    AUDIT_LOGS {
        int log_id PK
        int user_id FK
        string action
        text description
        datetime log_time
    }

    FAILED_LOGINS {
        int id PK
        string username
        string ip_address
        datetime attempt_time
    }
```

## DFD Level 0

```mermaid
flowchart LR
    U[User / Admin / Manager / Employee] --> A((Encrypted DBMS Web App))
    A --> M[(MySQL Database)]
    M --> A
    A --> U
```

## DFD Level 1

```mermaid
flowchart LR
    U[Authenticated User]
    AD[Admin]
    APP((Flask Application))
    AUTH[[1.0 Authentication]]
    CRUD[[2.0 Customer Management]]
    AUD[[3.0 Audit Logging]]
    DASH[[4.0 Security Dashboard]]
    DB[(MySQL Database)]

    U --> AUTH
    AD --> AUTH
    AUTH --> APP
    APP --> CRUD
    APP --> AUD
    APP --> DASH
    CRUD --> DB
    AUD --> DB
    DASH --> DB
    DB --> CRUD
    DB --> AUD
    DB --> DASH
```

## Use Case Diagram

```mermaid
flowchart LR
    Admin[Admin]
    Manager[Manager]
    Employee[Employee]

    UC1((Login / Logout))
    UC2((Register))
    UC3((Add Customer))
    UC4((View Customer))
    UC5((Edit Customer))
    UC6((Delete Customer))
    UC7((Search Customer))
    UC8((View Audit Logs))
    UC9((Manage Users))
    UC10((View Security Dashboard))

    Admin --> UC1
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10

    Manager --> UC1
    Manager --> UC3
    Manager --> UC4
    Manager --> UC5
    Manager --> UC6
    Manager --> UC7
    Manager --> UC8
    Manager --> UC10

    Employee --> UC1
    Employee --> UC2
    Employee --> UC3
    Employee --> UC4
    Employee --> UC5
    Employee --> UC7
    Employee --> UC10
```

## Notes

- The database stores customer fields in encrypted form.
- Search is performed after decryption in the application layer for authorized users.
- MySQL triggers write insert, update, and delete events into the audit trail.
