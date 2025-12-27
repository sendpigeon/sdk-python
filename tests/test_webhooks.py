import json
import hmac
import hashlib
import time

from sendpigeon import verify_webhook, verify_inbound_webhook


def create_signature(payload: str, timestamp: str, secret: str) -> str:
    """Create a valid webhook signature for testing."""
    signed_payload = f"{timestamp}.{payload}"
    return hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class TestVerifyWebhook:
    def test_valid_signature(self):
        secret = "whsec_test123"
        timestamp = str(int(time.time()))
        payload = json.dumps({"type": "email.delivered", "data": {"id": "em_123"}})
        signature = create_signature(payload, timestamp, secret)

        result = verify_webhook(
            payload=payload,
            signature=signature,
            timestamp=timestamp,
            secret=secret,
        )

        assert result.valid is True
        assert result.payload["type"] == "email.delivered"

    def test_invalid_signature(self):
        secret = "whsec_test123"
        timestamp = str(int(time.time()))
        payload = json.dumps({"type": "email.delivered"})

        result = verify_webhook(
            payload=payload,
            signature="invalid_signature",
            timestamp=timestamp,
            secret=secret,
        )

        assert result.valid is False
        assert result.error == "Invalid signature"

    def test_expired_timestamp(self):
        secret = "whsec_test123"
        timestamp = str(int(time.time()) - 600)  # 10 minutes ago
        payload = json.dumps({"type": "email.delivered"})
        signature = create_signature(payload, timestamp, secret)

        result = verify_webhook(
            payload=payload,
            signature=signature,
            timestamp=timestamp,
            secret=secret,
            max_age=300,  # 5 minutes
        )

        assert result.valid is False
        assert result.error == "Timestamp too old"

    def test_invalid_timestamp(self):
        result = verify_webhook(
            payload="{}",
            signature="sig",
            timestamp="invalid",
            secret="secret",
        )

        assert result.valid is False
        assert result.error == "Invalid timestamp"

    def test_invalid_json(self):
        secret = "whsec_test123"
        timestamp = str(int(time.time()))
        payload = "not valid json"
        signature = create_signature(payload, timestamp, secret)

        result = verify_webhook(
            payload=payload,
            signature=signature,
            timestamp=timestamp,
            secret=secret,
        )

        assert result.valid is False
        assert result.error == "Invalid JSON payload"

    def test_bytes_payload(self):
        secret = "whsec_test123"
        timestamp = str(int(time.time()))
        payload = json.dumps({"type": "test"})
        signature = create_signature(payload, timestamp, secret)

        result = verify_webhook(
            payload=payload.encode("utf-8"),
            signature=signature,
            timestamp=timestamp,
            secret=secret,
        )

        assert result.valid is True
        assert result.payload["type"] == "test"


class TestVerifyInboundWebhook:
    def test_valid_inbound_webhook(self):
        secret = "whsec_inbound"
        timestamp = str(int(time.time()))
        payload = json.dumps({
            "type": "inbound.received",
            "data": {
                "from": "sender@example.com",
                "to": "inbox@yourdomain.com",
                "subject": "Hello",
            },
        })
        signature = create_signature(payload, timestamp, secret)

        result = verify_inbound_webhook(
            payload=payload,
            signature=signature,
            timestamp=timestamp,
            secret=secret,
        )

        assert result.valid is True
        assert result.payload["data"]["from"] == "sender@example.com"
