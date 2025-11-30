# Password Reset Implementation

## Overview

Secure password reset feature with 30-minute token expiration, single-use tokens, and automatic session invalidation.

## Database Schema

**New Table: `password_reset_tokens`**
```python
- id: String (primary key)
- user_id: Integer (FK to users.user_id)
- hashed_token: String (unique, bcrypt hashed)
- expires_at: DateTime (30 min from creation)
- used: Boolean (single-use flag)
- created_at: DateTime
- ip_address: String (optional, for audit)
```

## API Endpoints

### 1. POST `/auth/request-reset`
Request a password reset token. Email is sent with reset link.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (always same to prevent account enumeration):**
```json
{
  "message": "If this email exists, we've sent a reset link."
}
```

**Status:** 200 OK

**Security Features:**
- Generic response (doesn't leak if email exists)
- Rate limit: 3 requests/hour per user
- IP tracking for audit
- 30-minute expiration

---

### 2. GET `/auth/verify-reset-token?token=...`
Verify token validity before showing reset form.

**Query Parameters:**
- `token`: The reset token from email link

**Response (valid):**
```json
{
  "valid": true,
  "user_id": 123
}
```

**Response (invalid/expired):**
```json
{
  "valid": false,
  "message": "Token expired"
}
```

**Status:** 200 OK (valid) or 401 (invalid)

---

### 3. POST `/auth/reset-password`
Reset the password using the token.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successful. Please login with your new password.",
  "user_id": 123
}
```

**Status:** 200 OK

**Security Features:**
- Token consumed (single-use only)
- All other reset tokens invalidated
- All sessions cleared (force re-login)
- Password must be 8+ characters
- Token must not be expired

---

## Email Configuration

### Gmail Setup (Recommended for Dev/Test)

1. **Enable 2FA** on Google Account
2. **Create App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password
3. **Set `.env`:**
   ```env
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  (app password)
   SMTP_FROM_EMAIL=your-email@gmail.com
   FRONTEND_URL=http://localhost:3000
   ```

### Other SMTP Providers

Update `.env` accordingly:
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@your-domain.com
```

### Testing Without Email (Development)

If SMTP credentials aren't set, tokens are logged to console:
```
Email not configured. Reset token created but not sent.
Debug: Reset token for user@example.com: <raw-token-here>
```

Copy the token and use it in requests.

---

## Frontend Integration

### Reset Password Flow

1. **User clicks "Forgot Password"**
   ```javascript
   POST /auth/request-reset
   { email: "user@example.com" }
   // Returns generic message
   ```

2. **User checks email, clicks link**
   ```
   http://localhost:3000/reset-password?token=<token>
   ```

3. **Frontend verifies token**
   ```javascript
   GET /auth/verify-reset-token?token=<token>
   // If valid, show reset form
   // If expired, show error
   ```

4. **User submits new password**
   ```javascript
   POST /auth/reset-password
   {
     token: "<token>",
     new_password: "NewPassword123"
   }
   // Clear auth cookies and redirect to login
   ```

---

## Security Properties

###  What We Do Right

1. **Token Storage**
   - Raw tokens NEVER stored in DB
   - Only bcrypt hashed versions stored
   - Even DB breach won't expose reset links

2. **Expiration**
   - 30-minute hard limit
   - Checked on every validation
   - Expired tokens can't be reused

3. **Single-Use**
   - Each token marked `used=True` after reset
   - Attempting to reuse fails
   - Prevents replay attacks

4. **Account Enumeration Prevention**
   - Same response for existing/non-existing emails
   - Silent failures on rate limit
   - Logs internally only

5. **Session Invalidation**
   - `last_login` cleared (force re-auth)
   - All existing sessions invalidated
   - Stops attacker with compromised session

6. **Rate Limiting**
   - 3 requests/hour per user
   - 5 requests/hour per IP (simplified, use Redis in production)

7. **Audit Trail**
   - IP addresses logged with tokens
   - Creation timestamp recorded
   - Success/failure logged to stdout

---



## Testing

### Manual Testing with cURL

1. **Request Reset**
```bash
curl -X POST http://localhost:5000/auth/request-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

2. **Check console for token** (if email not configured)

3. **Verify Token**
```bash
curl "http://localhost:5000/auth/verify-reset-token?token=<token-from-console>"
```

4. **Reset Password**
```bash
curl -X POST http://localhost:5000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "<token>", "new_password": "NewPass123"}'
```


---


## Troubleshooting

### Email not sending

1. Check SMTP credentials in `.env`
2. If Gmail: Ensure App Password (not regular password)
3. Check firewall allows port 587
4. Verify `SMTP_FROM_EMAIL` is correct

### Token validation failing

1. Verify token hasn't expired (30 min max)
2. Check token wasn't already used
3. Ensure exact token string (no spaces)
4. Check `used` flag in DB

### Rate limiting blocking legitimate requests

1. Current implementation uses in-memory DB queries
2. For production, implement Redis-based rate limiter
3. Adjust limits in `request_password_reset()` function

---

## Future Enhancements

1. **HMAC-signed tokens** - Prevent tampering without DB lookup
2. **Device fingerprinting** - Only reset from known devices
3. **Notification on password change** - "If this wasn't you, click here"
4. **IP-based token binding** - Restrict token to requesting IP
5. **Turnsile/ReCAPTCHA** - Before sending reset email
6. **Passwordless login** - Replace password reset with magic links
