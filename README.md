# Email Inbox Placement Tester

A production-ready desktop/web application for testing email deliverability across your own Gmail accounts. Automatically sends test emails and detects folder placement (Inbox, Promotions, Spam, etc.).

## Features

✅ **Gmail Account Management** - Add unlimited Gmail accounts via OAuth 2.0  
✅ **Test Email Creation** - Define subject, HTML/plaintext body, custom headers  
✅ **Bulk Sending** - Send one test email to multiple Gmail accounts  
✅ **Inbox Detection** - Automatically detect folder placement (Inbox, Promotions, Social, Updates, Spam, Trash)  
✅ **Real-time Dashboard** - Live scanning updates with WebSocket support  
✅ **Statistics & Charts** - Inbox %, Spam %, delivery times, trends  
✅ **Test History** - Store unlimited tests with search and comparison  
✅ **Export Reports** - CSV, Excel, PDF, JSON formats  
✅ **Performance Optimized** - Async/concurrent API requests with rate limit handling  
✅ **Security** - Encrypted OAuth tokens, no password storage  

## Technology Stack

**Backend**
- Python 3.12+
- FastAPI with async support
- SQLAlchemy ORM
- SQLite (upgradeable to PostgreSQL)
- Gmail API v1
- AsyncIO with concurrent.futures

**Frontend**
- React 18+
- Tailwind CSS
- Recharts for visualization
- Vite build tool

**Infrastructure**
- Docker & Docker Compose
- Alembic for migrations
- Pydantic for data validation
- Python-jose for JWT tokens

## Project Structure

```
inbox-placement-tester/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration management
│   │   ├── dependencies.py         # Dependency injection
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── routers/                # API endpoints
│   │   ├── services/               # Business logic
│   │   │   ├── gmail_auth.py      # OAuth 2.0 handling
│   │   │   ├── gmail_sender.py    # Email sending
│   │   │   ├── gmail_scanner.py   # Inbox detection
│   │   │   ├── test_runner.py     # Test orchestration
│   │   │   └── report_generator.py # Report generation
│   │   ├── utils/
│   │   │   ├── encryption.py      # Token encryption
│   │   │   ├── logging.py         # Structured logging
│   │   │   └── email_parser.py    # Email utility functions
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── db.py              # Session management
│   │       └── models.py          # ORM models
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Cloud project with Gmail API enabled
- Redis (optional, for advanced caching)

### Setup

1. **Clone and setup backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Create .env file**
```bash
cp ../.env.example ../.env
# Edit .env with your Google OAuth credentials
```

3. **Initialize database**
```bash
alembic upgrade head
```

4. **Run backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Setup frontend**
```bash
cd ../frontend
npm install
npm run dev
```

6. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### With Docker

```bash
docker-compose up --build
```

## Configuration

See `.env.example` for all available configuration options:
- Gmail API credentials
- Database connection
- JWT secret
- Encryption key
- SMTP settings (optional)

## API Endpoints

### Gmail Accounts
- `GET /api/accounts` - List connected Gmail accounts
- `POST /api/accounts/connect` - Start OAuth flow
- `DELETE /api/accounts/{account_id}` - Remove account

### Test Campaigns
- `POST /api/tests` - Create new test
- `GET /api/tests` - List all tests
- `GET /api/tests/{test_id}` - Get test details
- `POST /api/tests/{test_id}/send` - Send test emails
- `DELETE /api/tests/{test_id}` - Delete test

### Scanning
- `GET /api/tests/{test_id}/scan` - Start scanning for messages
- `GET /api/tests/{test_id}/results` - Get scan results
- `WS /ws/tests/{test_id}` - WebSocket for live updates

### Reports
- `GET /api/tests/{test_id}/export?format=csv|pdf|excel|json` - Export results

## Security Considerations

1. **OAuth Tokens**
   - Encrypted at rest using Fernet cipher
   - Refresh tokens auto-renewed before expiry
   - Automatic revocation on account removal

2. **Data Protection**
   - No plaintext password storage
   - JWT authentication for API
   - CORS configured for frontend

3. **Rate Limiting**
   - Respects Gmail API quotas
   - Concurrent request throttling
   - Exponential backoff for retries

## Performance

- Handles 10-100+ Gmail accounts simultaneously
- Async/await patterns throughout
- Connection pooling for database
- Efficient message searching with Gmail query syntax

## Development

### Running Tests
```bash
cd backend
pytest -v
pytest --cov=app tests/
```

### Code Quality
```bash
black app/
isort app/
flake8 app/
mypy app/
```

### Database Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Deployment

See `Dockerfile` and `docker-compose.yml` for containerization.

Recommended production setup:
- Nginx reverse proxy
- PostgreSQL database
- Redis for caching
- SSL/TLS certificates
- Environment-based secrets

## Contributing

Follow PEP 8 style guide with Black formatter.
Write tests for new features.
Update documentation accordingly.

## License

Proprietary - Internal Use Only

## Support

For issues and feature requests, contact: amanda@seoleads.me
