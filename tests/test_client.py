import pytest
from pytest_httpx import HTTPXMock

from sendpigeon import SendPigeon, AsyncSendPigeon


class TestSendPigeon:
    def test_send_email_success(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            json={"id": "em_123", "status": "sent"},
        )

        client = SendPigeon("sk_test_xxx")
        result = client.send(
            to="user@example.com",
            subject="Hello",
            html="<p>Hi</p>",
        )

        assert result.ok
        assert result.data.id == "em_123"
        assert result.data.status == "sent"

    def test_send_email_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            status_code=403,
            json={"message": "Domain not verified", "code": "DOMAIN_NOT_VERIFIED"},
        )

        client = SendPigeon("sk_test_xxx")
        result = client.send(
            to="user@example.com",
            subject="Hello",
            html="<p>Hi</p>",
        )

        assert not result.ok
        assert result.error.message == "Domain not verified"
        assert result.error.api_code == "DOMAIN_NOT_VERIFIED"
        assert result.error.status == 403

    def test_send_with_all_options(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            json={"id": "em_456", "status": "scheduled", "scheduled_at": "2024-01-15T10:00:00Z"},
        )

        client = SendPigeon("sk_test_xxx")
        result = client.send(
            to=["a@example.com", "b@example.com"],
            subject="Hello",
            html="<p>Hi</p>",
            text="Hi",
            from_address="sender@domain.com",
            cc="cc@example.com",
            bcc="bcc@example.com",
            reply_to="reply@example.com",
            tags=["test"],
            metadata={"key": "value"},
            scheduled_at="2024-01-15T10:00:00Z",
        )

        assert result.ok
        assert result.data.scheduled_at == "2024-01-15T10:00:00Z"

    def test_templates_list(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sendpigeon.dev/v1/templates",
            json=[
                {
                    "id": "tmpl_1",
                    "name": "Welcome",
                    "subject": "Welcome!",
                    "html": "<p>Hi</p>",
                    "variables": ["name"],
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z",
                }
            ],
        )

        client = SendPigeon("sk_test_xxx")
        result = client.templates.list()

        assert result.ok
        assert len(result.data) == 1
        assert result.data[0].name == "Welcome"

    def test_domains_create(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/domains",
            json={
                "id": "dom_1",
                "name": "example.com",
                "status": "pending",
                "createdAt": "2024-01-01T00:00:00Z",
                "dnsRecords": [
                    {"type": "TXT", "name": "_dkim.example.com", "value": "v=DKIM1;..."}
                ],
            },
        )

        client = SendPigeon("sk_test_xxx")
        result = client.domains.create("example.com")

        assert result.ok
        assert result.data.name == "example.com"
        assert len(result.data.dns_records) == 1

    def test_context_manager(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sendpigeon.dev/v1/templates",
            json=[],
        )

        with SendPigeon("sk_test_xxx") as client:
            result = client.templates.list()
            assert result.ok

    def test_unwrap_success(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            json={"id": "em_123", "status": "sent"},
        )

        client = SendPigeon("sk_test_xxx")
        email = client.send(to="user@example.com", subject="Hi", html="<p>Hi</p>").unwrap()

        assert email.id == "em_123"

    def test_unwrap_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            status_code=403,
            json={"message": "Error", "code": "ERROR"},
        )

        client = SendPigeon("sk_test_xxx")

        with pytest.raises(Exception) as exc_info:
            client.send(to="user@example.com", subject="Hi", html="<p>Hi</p>").unwrap()

        assert "Error" in str(exc_info.value)


class TestAsyncSendPigeon:
    @pytest.mark.asyncio
    async def test_send_email_success(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sendpigeon.dev/v1/emails",
            json={"id": "em_123", "status": "sent"},
        )

        async with AsyncSendPigeon("sk_test_xxx") as client:
            result = await client.send(
                to="user@example.com",
                subject="Hello",
                html="<p>Hi</p>",
            )

        assert result.ok
        assert result.data.id == "em_123"

    @pytest.mark.asyncio
    async def test_templates_list(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sendpigeon.dev/v1/templates",
            json=[],
        )

        client = AsyncSendPigeon("sk_test_xxx")
        result = await client.templates.list()
        await client.close()

        assert result.ok
        assert result.data == []
