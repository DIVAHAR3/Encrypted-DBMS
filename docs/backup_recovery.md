# Backup and Recovery Module

This project uses standard MySQL backup and restore utilities.

## Backup

```bash
mysqldump -u root -p encrypted_dbms > encrypted_dbms_backup.sql
```

For a compressed backup:

```bash
mysqldump -u root -p encrypted_dbms | gzip > encrypted_dbms_backup.sql.gz
```

## Recovery

```bash
mysql -u root -p encrypted_dbms < encrypted_dbms_backup.sql
```

For a compressed backup:

```bash
gunzip < encrypted_dbms_backup.sql.gz | mysql -u root -p encrypted_dbms
```

## Recommended Schedule

- Daily logical backup using `mysqldump`
- Weekly restore test in a staging environment
- Monthly integrity verification of encrypted customer records
