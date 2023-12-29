from pydantic import EmailStr
from core.model.token_model import *
from core.connection.cache_connection import redis
import logging
from datetime import timedelta, timezone
from core.utils.settings import settings
from core.model.cache_model import Cache
from core.event.produce_event import produce_event
from core.utils.init_log import logger
from core.helper.encryption_helper import encrypt
from core.model.otp_model import OTP
from fastapi import HTTPException, status
import json


async def get_account_from_cache(id: str):
    logger.info(f'Fetching account:{id} from cache')

    # Create key
    key = f"account:{id}"

    try:
        # Get account from cache
        account_bytes = await redis.get(key.encode())
        
        if not account_bytes:
            logger.warning(f"Account:{id} not fount in cache.")
            return None
        
        logger.info(f"Account:{id} found in cache.")
        logger.info(f"Deserializing account:{id}")
        
        # Deserialize
        account_data = json.loads(s=account_bytes)

        return account_data
    except Exception as err:
        logger.error(f"Failed to retrieve account:{id} from cache due to error:{str(err)}")


async def auth_token_exists(auth_token: str, email: EmailStr) -> dict:
    key = f"auth_token:{email}-{auth_token}"
    try:
        logger.info(f"Fetching auth token for {email}")
        auth_token = await redis.get(key.encode())
        if auth_token:
            logger.info('Auth token found.')
            return True
        logger.warning('Auth token not found', exc_info=1)
        return False        
    except Exception as err:
        logger.error(f'Failed to retrieve auth token due to error: {str(err)}', exc_info=1)
        return False


async def is_revoked_token(token: str, account_id: str) -> dict:
    # Encrypt token
    encrypted_otp = encrypt(value=token)

    key = f"refresh_token:{account_id}-{encrypted_otp}"
    
    try:
        logger.info('Fetching revoked token')
        revoked_token = await redis.get(key.encode())
        if revoked_token:
            logger.info('Refresh token was revoked.')
            return True
        logger.info('Refresh token valid.')
        return False        
    except Exception as err:
        logger.error(f'Failed to verify refresh token due to err{str(err)}.', exc_info=1)
        return False
    

async def is_valid_otp(verify_otp: VerifyOTP):
    # Encrypt OTP
    encrypted_otp = encrypt(value=verify_otp.one_time_password)
    
    # Retrieve the otp
    key = f"otp:{verify_otp.email}-{encrypted_otp}-{verify_otp.purpose.lower()}"
    try:  
        logger.info('fetching one time password.')
        
        # Fetch otp
        otp_exists_bytes = await redis.get(key.encode())
        
        # Check if otp does not exists
        if not otp_exists_bytes:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid one-time-password'
        )
        
        logger.info('OTP found.')
        
        # Deserialize OTP
        otp_obj = OTP.deserialize(data=otp_exists_bytes)

        # Check if OTP have expired
        logger.info('Checking if OTP have expired.')

        if datetime.now(timezone.utc) >= otp_obj.expires_on:
            logger.info('Expired OTP')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expired One-Time-Password"
            )
        
        return True
            
    except Exception as err:
        logger.error(f'Failed to validate OTP due to error {str(err)}')


async def cache_auth_token_event(token: str, email: EmailStr):
    # Create auth token obj
    auth_token_obj = AuthToken(
        token=token,
        email=email,
        expiry= datetime.utcnow() + timedelta(seconds=settings.api_auth_token_expiry)
    )

    # Serialize
    auth_token_event = auth_token_obj.serialize()

    # Create cache key
    key = f"auth_token:{email}-{token}"

    # Create cache obj
    cache_obj = Cache(key=key, data=auth_token_event)

    # Serialize cache
    cache_event = cache_obj.serialize()

    # Emit event
    await produce_event(topic=settings.api_cache_topic, value=cache_event)


async def is_valid_auth_token(email: EmailStr, token: str) -> None:
    # encypt auth token
    encrypted_token = encrypt(value=token)

    # Declare the key
    key = f"auth_token:{email}-{encrypted_token}"

    try:
        # Get the auth token if it exists
        auth_token_byte = await redis.get(key.encode()) 
        
        # Check if auth token is None
        if not auth_token_byte:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Invalid auth token.'
        )
        
        # Deserialize auth token
        auth_token_obj = AuthToken.deserialize(auth_token_byte)

        # Check if auth token have expired
        if datetime.now(timezone.utc) >= auth_token_obj.expiry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expired auth token"
        )
        return True        
    except Exception as err:
        logging.error(f'Failed to verify auth token due to error: {str(err)}')
