# RMS Backend Setup Guide

## Initial Setup

### 1. Create Virtual Environment
```bash
cd RMS-BACKEND
pipenv install
pipenv shell
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4. Run Development Server
```bash
python app.py
```

Server runs on `http://localhost:5000`

---

## Password Reset Feature

### Email Setup (for sending reset links)

**Option 1: Gmail (Recommended for Dev)**
1. Enable 2FA on Google Account
2. Create App Password at: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```env
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=<16-char app password>
   ```

**Option 2: Other SMTP Provider**
- Update `SMTP_SERVER`, `SMTP_PORT`, etc. in `.env`

**Option 3: Skip Email (Development)**
- Leave `SMTP_USERNAME` and `SMTP_PASSWORD` blank
- Tokens will be printed to console
- Use them manually for testing

### API Endpoints

```
POST   /auth/request-reset          # Request password reset
GET    /auth/verify-reset-token     # Validate token
POST   /auth/reset-password         # Reset with new password
```

See `PASSWORD_RESET.md` for detailed docs.

---

## Project Structure

```
RMS-BACKEND/
├── app.py                  # Main Flask app & routes
├── models.py               # Database models (+ PasswordResetToken)
├── config.py               # Flask configuration
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Template for .env
├── Pipfile                 # Python dependencies
├── Pipfile.lock            # Locked dependency versions
├── PASSWORD_RESET.md       # Password reset detailed docs
├── SETUP.md                # This file
└── instance/
    └── rms.db              # SQLite database (created automatically)
```

---

## API Quick Reference

### Authentication
```bash
# Register
POST /register
{ "username": "", "email": "", "password": "", "role": "", "is_active": true }

# Login
POST /login
{ "email": "", "password": "" }
# Returns cookie 'user' with user data

# Logout
POST /logout
```

### Password Reset
```bash
# Step 1: Request reset
POST /auth/request-reset
{ "email": "user@example.com" }

# Step 2: Verify token (from email link)
GET /auth/verify-reset-token?token=<token>

# Step 3: Reset password
POST /auth/reset-password
{ "token": "<token>", "new_password": "NewPass123" }
```


## Database Schema (New)

### password_reset_tokens
- `id`: String (PK)
- `user_id`: Integer (FK)
- `hashed_token`: String (unique)
- `expires_at`: DateTime (30 min from creation)
- `used`: Boolean (single-use flag)
- `created_at`: DateTime
- `ip_address`: String (optional)

---

## Troubleshooting

### Import Errors
```bash
pipenv install  # Reinstall all dependencies
```

### Database Issues
```bash
# Reset database (CAREFUL - deletes all data)
rm instance/rms.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Port Already in Use
```bash
python app.py --port 5001
```

### Email Not Sending
1. Check SMTP credentials in `.env`
2. For Gmail: Use App Password, not regular password
3. Check firewall allows port 587
4. Look for errors in console output

---

## Production Deployment

1. Set `FLASK_ENV=production`
2. Generate strong `SECRET_KEY`
3. Use production database (PostgreSQL recommended)
4. Configure real SMTP service
5. Enable HTTPS
6. Use Redis for rate limiting
7. Set `FRONTEND_URL` to production domain
8. Run with gunicorn: `gunicorn -w 4 app:app`

---

## Development Tips

**Debug Password Reset Tokens:**
```python
from app import app, db
from models import PasswordResetToken
app.app_context().push()
tokens = PasswordResetToken.query.all()
for t in tokens:
    print(f"User {t.user_id}: expires {t.expires_at}, used={t.used}")
```

**Check Reset Email in Console (dev mode):**
- When SMTP not configured, tokens print to stdout
- Copy token and test with cURL or frontend

---

## Next Steps

1. Review `PASSWORD_RESET.md` for security details
2. Set up email (Gmail recommended for dev)
3. Test endpoints with cURL or Postman
4. Integrate frontend login/reset forms
5. Configure CORS for frontend URL
