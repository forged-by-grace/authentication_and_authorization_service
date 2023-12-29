from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from app.main import app
from core.utils.settings import settings
from core.helper.request_helper import send_post_request


# Account registration url
account_url: str = '/api/v1/auth/login/email/'

# Test account login credentials
test_login_credentials = {
        "password": "stringst123",
        "device_info": {
            "device_name": "Samsong s23 ultra",
            "platform": "IOS",
            "ip_address": "127.0.0.1",
            "device_model": "string",
            "device_id": "string",
            "screen_info": {
                "height": 1920,
                "width": 720,
                "resolution": 1200
            },
            "device_serial_number": "124578963",
            "is_active": True
        },
        "email": "johndoe@example.com"
    }


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        print("client is ready")
        yield client


@pytest.mark.anyio
async def test_login_with_email_failed_account_not_found(client: httpx.AsyncClient):
    invalid_credentials: dict = {}
    invalid_credentials = test_login_credentials.copy()
    invalid_credentials.update({'email': 'user@example.com'})
    
    # Send request
    response = await client.post(account_url, json=invalid_credentials)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_login_with_email_failed_invalid_password(client: httpx.AsyncClient):
    invalid_credentials: dict = {}
    invalid_credentials = test_login_credentials.copy()
    invalid_credentials.update({'password': 'user@example.com'})
    
    # Send request
    response = await client.post(account_url,json=invalid_credentials)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_login_with_email_failed_email_not_verified(client: httpx.AsyncClient):
    invalid_credentials: dict = {}
    invalid_credentials = test_login_credentials.copy()
    invalid_credentials.update({'email': 'johndoe1@example.com'})
    
    # Send request
    response = await client.post(account_url,json=invalid_credentials)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_login_with_email_failed_active_devices_greater_than_five(client: httpx.AsyncClient):

    # Send request
    response = await client.post(account_url,json=test_login_credentials)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_login_with_email_successful(client: httpx.AsyncClient):

    # Send request
    response = await client.post(account_url,json=test_login_credentials)

    assert response.status_code == status.HTTP_200_OK
