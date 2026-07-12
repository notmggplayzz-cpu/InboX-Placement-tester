# API Reference

Base URL: `http://localhost:8000/api`

## Authentication

All endpoints require valid Gmail OAuth tokens. Tokens are encrypted and stored securely.

## Accounts API

### Get OAuth URL

Generate Google OAuth authorization URL.

```
GET /accounts/oauth-url?state=<user_id>
```

**Query Parameters:**
- `state` (required): Unique user identifier

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### OAuth Callback

Handle OAuth callback from Google.

```
POST /accounts/callback?code=<code>&state=<state>
```

**Query Parameters:**
- `code` (required): Authorization code from Google
- `state` (required): State parameter sent with initial request

**Response:**
```json
{
  "account_id": 1,
  "email": "user@gmail.com"
}
```

### List Accounts

Get all connected Gmail accounts.

```
GET /accounts
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@gmail.com",
    "nickname": "Personal Account",
    "is_active": true,
    "last_sync": "2024-01-15T10:30:00",
    "created_at": "2024-01-10T15:20:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### Get Account

Get specific Gmail account details.

```
GET /accounts/{account_id}
```

**Path Parameters:**
- `account_id` (required): Account ID

**Response:**
```json
{
  "id": 1,
  "email": "user@gmail.com",
  "nickname": "Personal Account",
  "is_active": true,
  "last_sync": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T15:20:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Update Account

Update Gmail account details.

```
PATCH /accounts/{account_id}
```

**Path Parameters:**
- `account_id` (required): Account ID

**Request Body:**
```json
{
  "nickname": "Work Account",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@gmail.com",
  "nickname": "Work Account",
  "is_active": true,
  "last_sync": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T15:20:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### Delete Account

Delete a Gmail account.

```
DELETE /accounts/{account_id}
```

**Path Parameters:**
- `account_id` (required): Account ID

**Response:**
```json
{
  "message": "Account deleted successfully"
}
```

## Tests API

### Create Test Campaign

Create a new test email campaign.

```
POST /tests
```

**Request Body:**
```json
{
  "campaign_name": "Q4 Newsletter",
  "subject": "Your Q4 Newsletter",
  "html_body": "<html><body>Newsletter content</body></html>",
  "plain_text_body": "Newsletter content",
  "sender_email": "newsletter@example.com",
  "custom_headers": "{\"X-Campaign-ID\": \"q4-2024\"}",
  "scheduled_time": null
}
```

**Response:**
```json
{
  "id": 1,
  "campaign_name": "Q4 Newsletter",
  "subject": "Your Q4 Newsletter",
  "sender_email": "newsletter@example.com",
  "status": "draft",
  "total_accounts": 0,
  "sent_time": null,
  "completed_time": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### List Test Campaigns

List all test campaigns with optional filtering.

```
GET /tests?status=<status>&limit=50&offset=0
```

**Query Parameters:**
- `status` (optional): Filter by status (draft, sending, sent, scanning, completed, failed)
- `limit` (optional): Maximum results (default: 50, max: 100)
- `offset` (optional): Skip N results (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "campaign_name": "Q4 Newsletter",
    "subject": "Your Q4 Newsletter",
    "sender_email": "newsletter@example.com",
    "status": "completed",
    "total_accounts": 5,
    "sent_time": "2024-01-15T10:30:00",
    "completed_time": "2024-01-15T10:35:00",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:35:00"
  }
]
```

### Get Test Campaign

Get specific test campaign details.

```
GET /tests/{campaign_id}
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
{
  "id": 1,
  "campaign_name": "Q4 Newsletter",
  "subject": "Your Q4 Newsletter",
  "sender_email": "newsletter@example.com",
  "status": "completed",
  "total_accounts": 5,
  "sent_time": "2024-01-15T10:30:00",
  "completed_time": "2024-01-15T10:35:00",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### Send Test

Send test emails to all active Gmail accounts.

```
POST /tests/{campaign_id}/send
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
{
  "sent": 5,
  "failed": 0,
  "total": 5,
  "campaign_id": 1
}
```

### Scan Test

Scan all Gmail accounts for test email placement.

```
POST /tests/{campaign_id}/scan
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
{
  "campaign_id": 1,
  "scanned": 5,
  "completed_at": "2024-01-15T10:35:00"
}
```

### Get Test Results

Get detailed results for a test campaign.

```
GET /tests/{campaign_id}/results
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
[
  {
    "id": 1,
    "campaign_id": 1,
    "account_id": 1,
    "email": "user@gmail.com",
    "folder": "INBOX",
    "received_time": "2024-01-15T10:31:00",
    "scanned_time": "2024-01-15T10:35:00",
    "delivery_time_seconds": 60.5,
    "scan_time_seconds": 2.3,
    "labels": "INBOX,UNREAD",
    "is_unread": true,
    "is_starred": false,
    "confidence": 1.0,
    "error_message": null,
    "retry_count": 0,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:35:00"
  }
]
```

### Get Test Statistics

Get aggregate statistics for a test campaign.

```
GET /tests/{campaign_id}/statistics
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
{
  "id": 1,
  "campaign_id": 1,
  "total_accounts": 5,
  "inbox_count": 4,
  "promotions_count": 1,
  "social_count": 0,
  "updates_count": 0,
  "spam_count": 0,
  "trash_count": 0,
  "not_found_count": 0,
  "inbox_percentage": 80.0,
  "spam_percentage": 0.0,
  "delivery_rate": 100.0,
  "average_delivery_time": 55.5,
  "average_scan_time": 2.1,
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### Delete Test Campaign

Delete a test campaign and all associated results.

```
DELETE /tests/{campaign_id}
```

**Path Parameters:**
- `campaign_id` (required): Campaign ID

**Response:**
```json
{
  "message": "Test campaign deleted"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Please fill in all required fields"
}
```

### 404 Not Found

```json
{
  "detail": "Test campaign not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to create test: Error message"
}
```

## Status Codes

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Folder Enums

Possible folder values in results:

- `INBOX` - Email arrived in main inbox
- `CATEGORY_PROMOTIONS` - Email filtered to Promotions tab
- `CATEGORY_SOCIAL` - Email filtered to Social tab
- `CATEGORY_UPDATES` - Email filtered to Updates tab
- `SPAM` - Email filtered to Spam folder
- `TRASH` - Email moved to Trash
- `NOT_FOUND` - Email not delivered

## Test Status Enums

Possible status values:

- `draft` - Test created but not sent
- `sending` - Emails are being sent
- `sent` - All emails sent
- `scanning` - Scanning accounts for placement
- `completed` - Scan completed
- `failed` - Test failed

## Rate Limiting

Gmail API has the following limits:

- **100 requests per user per 100 seconds**
- **500,000 requests per day per project**

The application respects these limits and queues requests accordingly.

## Pagination

Use `limit` and `offset` for pagination:

```
GET /tests?limit=10&offset=20
```

- Default limit: 50
- Maximum limit: 100
- Default offset: 0

## Sorting

Results are sorted by creation date (newest first) by default.

## Examples

### Complete Workflow

```bash
# 1. Get OAuth URL
curl -X GET "http://localhost:8000/api/accounts/oauth-url?state=user123"

# 2. Handle OAuth callback (redirected to)
# http://localhost:8000/api/accounts/callback?code=...&state=user123

# 3. List accounts
curl -X GET "http://localhost:8000/api/accounts"

# 4. Create test
curl -X POST "http://localhost:8000/api/tests" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Test",
    "subject": "Test Email",
    "html_body": "<html><body>Test</body></html>",
    "sender_email": "test@example.com"
  }'

# 5. Send test
curl -X POST "http://localhost:8000/api/tests/1/send"

# 6. Wait 10 seconds, then scan
curl -X POST "http://localhost:8000/api/tests/1/scan"

# 7. Get results
curl -X GET "http://localhost:8000/api/tests/1/results"

# 8. Get statistics
curl -X GET "http://localhost:8000/api/tests/1/statistics"
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
