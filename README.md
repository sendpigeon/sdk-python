# SendPigeon Python SDK

Official Python SDK for [SendPigeon](https://sendpigeon.dev) - Transactional Email API.

## Installation

```bash
pip install sendpigeon
```

## Quick Start

```python
from sendpigeon import SendPigeon

client = SendPigeon("sk_live_xxx")

# Send an email
result = client.send(
    to="user@example.com",
    subject="Welcome!",
    html="<h1>Hello!</h1><p>Welcome to our service.</p>"
)

if result.ok:
    print(f"Email sent: {result.data.id}")
else:
    print(f"Error: {result.error.message}")
```

## Async Support

```python
from sendpigeon import AsyncSendPigeon

async with AsyncSendPigeon("sk_live_xxx") as client:
    result = await client.send(
        to="user@example.com",
        subject="Hello",
        html="<p>Hi there!</p>"
    )
```

## Features

### Send Email

```python
result = client.send(
    to="user@example.com",       # or ["a@x.com", "b@x.com"]
    subject="Hello",
    html="<p>HTML content</p>",
    text="Plain text fallback",
    from_address="hello@yourdomain.com",
    reply_to="support@yourdomain.com",
    cc="cc@example.com",
    bcc="bcc@example.com",
    tags=["welcome", "onboarding"],
    metadata={"user_id": "123"},
    scheduled_at="2024-01-15T10:00:00Z",
)
```

### Templates

```python
# Use a template
result = client.send(
    to="user@example.com",
    template_id="tmpl_xxx",
    variables={"name": "John", "company": "Acme"},
)

# Manage templates
templates = client.templates.list()
template = client.templates.create(
    name="Welcome Email",
    subject="Welcome, {{name}}!",
    html="<p>Hi {{name}}, welcome to {{company}}!</p>"
)
```

### Batch Sending

```python
result = client.send_batch([
    {"to": "a@example.com", "subject": "Hi A", "html": "<p>Hello A</p>"},
    {"to": "b@example.com", "subject": "Hi B", "html": "<p>Hello B</p>"},
])

print(f"Sent: {result.data.summary['sent']}, Failed: {result.data.summary['failed']}")
```

### Domains

```python
# List domains
domains = client.domains.list()

# Add and verify a domain
domain = client.domains.create("yourdomain.com")
print(f"Add these DNS records: {domain.data.dns_records}")

# Check verification
verification = client.domains.verify(domain.data.id)
print(f"Verified: {verification.data.verified}")
```

### API Keys

```python
# Create a new API key
key = client.api_keys.create(
    name="Production",
    mode="live",
    permission="sending",  # or "full_access"
)
print(f"Save this key: {key.data.key}")  # Only shown once!

# List keys
keys = client.api_keys.list()
```

### Webhook Verification

```python
from sendpigeon import verify_webhook

result = verify_webhook(
    payload=request.body,
    signature=request.headers["X-Webhook-Signature"],
    timestamp=request.headers["X-Webhook-Timestamp"],
    secret="whsec_xxx",
)

if result.valid:
    event = result.payload
    print(f"Event: {event['type']}")
```

## Error Handling

The SDK uses a Result pattern - no exceptions are thrown for API errors:

```python
result = client.send(to="user@example.com", subject="Hi", html="<p>Hello</p>")

if result.error:
    print(f"Error: {result.error.message}")
    print(f"Code: {result.error.code}")      # "api_error", "network_error", "timeout_error"
    print(f"API Code: {result.error.api_code}")  # e.g., "DOMAIN_NOT_VERIFIED"
    print(f"Status: {result.error.status}")  # HTTP status code
else:
    print(f"Success: {result.data.id}")

# Or use unwrap() for quick scripts (raises on error)
email = client.send(...).unwrap()
```

## Configuration

```python
client = SendPigeon(
    "sk_live_xxx",
    base_url="https://api.sendpigeon.dev",  # Override API URL
    timeout=30.0,                            # Request timeout in seconds
    max_retries=2,                           # Retry failed requests (0-5)
    debug=True,                              # Log requests/responses
)
```

## License

MIT
