from pydantic import EmailStr
from fastapi import Request, HTTPException, status
from core.model.account_model import AccountInDB
from core.helper.token_helper import verify_token
from core.utils.settings import settings
from core.utils.init_log import logger
from core.model.cache_model import Cache
from core.event.produce_event import produce_event
from core.model.token_model import *
from core.model.account_model import *
from core.helper.password_helper import *
from core.enums.auth_enum import AuthType
from core.helper.db_helper import *
from core.helper.encryption_helper import encrypt
from core.utils.error import credential_error
from core.model.device_model import *
from core.helper.cache_helper import get_account_from_cache


async def cache_account(data: dict) -> None:
    account_obj = AccountInDB(**data)
    # Serialize
    account_event = account_obj.serialize()

    # Create cache model
    key = f"account:{account_obj.email}"
    cache_obj = Cache(key=key, data=account_event) 

    # Serialize cache
    cache_event = cache_obj.serialize()

    # Emit event
    logger.info('Emitting account cache event.')
    await produce_event(topic=settings.api_cache_topic, value=cache_event)


async def get_current_active_account(request: Request) -> dict:
    # Get access token
    if not request.headers.get('Authorization'):
        raise credential_error
    
    token_data = request.headers.get('Authorization')
      
    # Extract data
    token_type = token_data.split()[0]
    access_token = token_data.split()[1]

    # Check if token type is Bearer
    if not token_type or token_type.lower != 'bearer':
        raise credential_error
    
    # Check if access token was provided
    if not access_token:
        raise credential_error
    
    # Verify access token
    current_account = await verify_token(token=access_token, secret=settings.api_access_token_secret)
    if not current_account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token'
        )
    
    return current_account



async def authenticate_account(device_ip: str, data, auth_type: str) -> AccountInDB:
    # initialize account dict
    account_exists = {}

    # Validate email
    if auth_type == AuthType.email.value:
        account_exists = await get_account_by_email(email=data.email)
    elif auth_type == AuthType.phone.value:
        account_exists = await get_account_by_phone_number(phone_number=data.phone_number)
  
    # Check if account exists
    logger.info('Checking if account exists.')
    if not account_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account not found"
        )
    
    # Check if email is verified
    logger.info("Checking if email is verified.")
    if (auth_type == AuthType.email.value) and  not account_exists.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email not verified.'
        )
    
    # Check if phone number is verified
    logger.info('Checking if phone number is verified.')
    if (auth_type == AuthType.phone.value) and  not account_exists.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Phone number not verified.'
        )
    
    # Check if active devices are greater than 5
    logger.info('Checking number of active devices exceeds 5')
    if account_exists.active_device_count > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only five devices can log in simulteneously"
        )
    
    # Check if device is already logged in
    # logger.info("Checking if device is already logged in.")
    # if device_ip in account_exists.active_devices:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Account already logged-in on this device."
    #     )
 
    # Verifying password
    logger.info('Verifying password')
    is_valid = verify_password(hashed_password=account_exists.hashed_password, plain_password=data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid password"
        )

    return account_exists
  

async def logout_event(email: EmailStr, token: str):
    # Create obj
    logout_obj = Logout(email=email, refresh_token=token)

    # Serialize
    logout_event = logout_obj.serialize()
    await produce_event(topic=settings.api_logout_topic, value=logout_event)


def has_token(request: Request) -> str:
    if not request.headers.get('Authorization'):
        return None
    
    token_data = request.headers.get('Authorization')
    token_type = token_data.split()[0]
    token = token_data.split()[1] 

    logger.info(f"Checking if token-type is 'Bearer'.")
    if not token_type or token_type != settings.api_token_type:
        return None

    # Check if token is present in header
    logger.info(f"Checking if token is None.")
    if not token:
        return None  
    
    logger.info(f"Token found in header.")

    return token


async def update_account(email: EmailStr, id: str, device_ip: str, token: str, device_data):
    # Encrypt refresh token
    logger.info('Encypting refresh token')
    encrypted_token = encrypt(value=token)

    # Create assign token obj
    assign_token_obj = AssignToken(
        id=id,
        email=email,
        device_ip=device_ip,
        token=encrypted_token,
        device_info=device_data
    )
    
    # Serialize
    assign_token_event = assign_token_obj.serialize()

    # Emit event
    logger.info('Emitting assign token event.')
    await produce_event(topic=settings.api_assign_token, value=assign_token_event)


