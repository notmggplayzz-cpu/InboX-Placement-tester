# Setup Guide - Email Inbox Placement Tester

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn
- Google Cloud project with Gmail API enabled
- Git

## Step 1: Google Cloud Setup

### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project named "Inbox Placement Tester"
3. Enable the following APIs:
   - Gmail API
   - Google Drive API (optional, for email attachments)

### Create OAuth 2.0 Credentials

1. Navigate to "Credentials" in the left sidebar
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Add authorized JavaScript origins:
   - `http://localhost:5173`
   - `http://localhost:3000`
   - `http://localhost:8000`
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/accounts/callback`
6. Copy the Client ID and Client Secret

## Step 2: Backend Setup

```bash
cd inbox-placement-tester/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Environment Configuration

```bash
cd ..
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./inbox_tester.db

# Gmail API
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/accounts/callback

# JWT & Encryption
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-32-chars-long!

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Other settings (keep defaults or adjust as needed)
```

Generate secure keys:

```bash
# For JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# For ENCRYPTION_KEY (must be 32 chars)
python -c "import secrets; print(secrets.token_urlsafe(24)[:32])"
```

## Step 4: Database Setup

```bash
cd backend

# Initialize database
python -c "from app.database import init_db; init_db()"

# If using Alembic (recommended for production)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Step 5: Run Backend

```bash
# From backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be accessible at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

## Step 6: Frontend Setup

In a new terminal:

```bash
cd inbox-placement-tester/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend should be accessible at: `http://localhost:5173`

## Step 7: Test the Application

1. Open `http://localhost:5173` in your browser
2. Click "Accounts" → "Connect Account"
3. Sign in with your Gmail account
4. Grant permissions when prompted
5. Create a test campaign
6. Send test emails
7. Scan accounts for email placement

## Docker Deployment

### Build and Run with Docker Compose

```bash
docker-compose up --build
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Running Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

## Code Quality

```bash
cd backend

# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Production Deployment

### 1. Security Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Generate new `ENCRYPTION_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Configure logging

### 2. Database Migration (PostgreSQL)

```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost/inbox_tester

# Run migrations
alembic upgrade head
```

### 3. Deploy with Docker

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Nginx Configuration

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name inbox-tester.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Issue: "No module named 'app'"

**Solution:** Ensure you're in the `backend` directory and the virtual environment is activated.

### Issue: "Port 8000 already in use"

**Solution:** 
```bash
lsof -i :8000  # Find process using port
kill -9 <PID>  # Kill the process
```

### Issue: Gmail API authentication fails

**Solution:**
1. Verify Client ID and Client Secret are correct
2. Check that OAuth redirect URI matches exactly
3. Enable Gmail API in Google Cloud Console
4. Try disconnecting and reconnecting the account

### Issue: Encryption key errors

**Solution:**
- Ensure `ENCRYPTION_KEY` is exactly 32 characters
- If you change the key, old encrypted tokens become invalid
- Generate new key only in development or clear all accounts in production

## Logs Location

- Backend logs: stdout/stderr
- Database: `./inbox_tester.db` (SQLite) or PostgreSQL
- Frontend logs: Browser console (F12)

## Performance Tuning

### For 50-100 Gmail Accounts

1. **Increase concurrent API requests:**
   ```env
   GMAIL_API_MAX_CONCURRENT=10
   ```

2. **Database optimization:**
   ```env
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=40
   ```

3. **Frontend caching:**
   - Enable Redis in production
   - Use browser caching

4. **Rate limiting:**
   - Respect Gmail API quotas (1000 requests/user/100 seconds)
   - Implement request queuing for large batch operations

## Next Steps

1. Read the [API Documentation](./README.md#api-endpoints)
2. Explore the [Frontend Components](./frontend/src/components)
3. Check the [Database Schema](./backend/app/database/models.py)
4. Review [Security Best Practices](./README.md#security-considerations)

## Support

For issues, feature requests, or questions:
- Email: amanda@seoleads.me
- GitHub Issues: (if using version control)

## License

Proprietary - Internal Use Only
