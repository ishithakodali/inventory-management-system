# Inventory Management System

## Admin-managed staff accounts

Staff accounts can only be created by an administrator from **Manage Users**. The account is created only after its credential email has been accepted by the configured SMTP server.

Configure SMTP before creating staff accounts. Set these environment variables in the process that starts Flask:

```bash
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="smtp-user"
export SMTP_PASSWORD="smtp-password"
export SMTP_FROM_EMAIL="inventory@example.com"
export SMTP_USE_TLS="true"
python app.py
```

`SMTP_PORT` defaults to `587` and `SMTP_USE_TLS` defaults to `true`. Never commit SMTP credentials; `.env` files are ignored and this project does not load them automatically.

The application adds the nullable `users.email` column and its case-insensitive unique index automatically at startup. Existing accounts remain usable: their legacy plaintext password is upgraded to a secure hash after their next successful login.

Run the automated checks with:

```bash
python -m unittest discover -s tests -v
```
