from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from app.main import app
from core.utils.settings import settings
from core.helper.request_helper import send_post_request


# Account registration url
account_url: str = '/api/v1/auth/auth-token/verify/'


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        print("client is ready")
        yield client


@pytest.mark.anyio
async def test_verify_auth_token_failed_invalid_auth_token(client: httpx.AsyncClient):
    # Test body
    test_body = {
            "email": "user@example.com",
            "auth_token": "string"
        }

    # Send request
    response = await client.post(account_url, json=test_body)

    assert response.status_code == status.HTTP_404_NOT_FOUND

