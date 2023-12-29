from datetime import datetime, timedelta
from core.utils.settings import settings
from jose import jwt, JWTError
from fastapi import HTTPException, status
import secrets
from core.helper.cache_helper import *
from pydantic import EmailStr
from core.event.produce_event import produce_event
from core.helper.get_account_helper import get_account_with_refresh_token
from core.helper.encryption_helper import encrypt
from core.utils.error import credential_error
from core.model.cache_model import InvalidateCache


def create_token(payload: dict, secret: str):
    # Encode token
    try:
        return jwt.encode(claims=payload, key=secret, algorithm=settings.api_algorithm)
    except Exception as err:
        logger.error(f'Failed to create token due to error: {str(err)}')


def verify_token(token: str, secret: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(
            token=token, 
            key=secret, 
            algorithms=settings.api_algorithm, 
            audience=settings.api_token_aud,
            subject=settings.api_token_sub,
            issuer=settings.api_token_iss
            )
        if not payload:
            raise credentials_exception 
        return payload
    except JWTError as err:
        logger.error(f'Failed to verify token due to error: {str(err)}')
        raise credentials_exception
    

def create_auth_token(bytes: int) -> str:
    return secrets.token_hex(bytes)


async def get_token_data(refresh_token: str):
    # Verify refresh token
    logger.info(f"Validating refresh token.")
    valid_refresh_token_data = verify_token(token=refresh_token, secret=settings.api_refresh_token_secret)
    if valid_refresh_token_data is None:
        logger.error('Invalid refresh token.')
        raise credential_error
    
    # Check if refresh token was revoked
    logger.info(f"Checking if refresh token have been previously revoked.")
    is_revoked = is_revoked_token(refresh_token=refresh_token, account_id=valid_refresh_token_data.get('_id'))
    if is_revoked:
        raise credential_error
    
    return True, valid_refresh_token_data


async def revoke_refresh_token(token: str, id: str, device_ip: str):
    # Encrypt token
    encrypted_token = encrypt(value=token)

    # Create revoke token obj
    revoke_token_obj = RevokeRefreshToken(id=id, token=encrypted_token, device_ip=device_ip)

    # Serialize token
    revoke_token_event = revoke_token_obj.serialize()
    
    # Emit event
    await produce_event(topic=settings.api_revoke_refresh_token_topic, value=revoke_token_event)


def generate_token_set(id: str, is_admin: bool, firstname: str, lastname: str, email: EmailStr):
    # Create token expiry
    access_token_exp = datetime.utcnow() + timedelta(seconds=settings.api_access_token_expiry)
    refresh_token_exp = datetime.utcnow() + timedelta(seconds=settings.api_refresh_token_expiry)
    
    # Create payload
    payload_access_token = {
        'iss': settings.api_token_iss,
        'aud': settings.api_token_aud,
        'sub': settings.api_token_sub,
        'firstname': firstname,
        'lastname': lastname,
        'email': email,
        'id': id,
        'admin': is_admin,
        'iat': datetime.utcnow(),
        'exp': access_token_exp
    }

    payload_refresh_token = {
        'iss': settings.api_token_iss,
        'aud': settings.api_token_aud,
        'sub': settings.api_token_sub,
        'firstname': firstname,
        'lastname': lastname,
        'email': email,
        'id': id,
        'admin': is_admin,
        'iat': datetime.utcnow(),
        'exp': refresh_token_exp
    }
    
    # Generate access token
    access_token = create_token(payload=payload_access_token, secret=settings.api_access_token_secret)
    refresh_token = create_token(payload=payload_refresh_token, secret=settings.api_refresh_token_secret)

    return access_token, refresh_token


async def is_reused_token(id: str, token: str) -> bool:
   
    # Check if token is in database
    account_data = await get_account_with_refresh_token(id=id, refresh_token=token)

    return account_data


async def invalidate_account_tokens(id: str):
    # Invalidating token
    logger.warning('Invalidating account tokens')

    # Create reused refresh token obj
    reuse_token = ReusedToken(id=id)

    # Serialize
    reuse_token_event = reuse_token.serialize()

    # Emit invalidate token event
    await produce_event(topic=settings.api_reused_refresh_token, value=reuse_token_event)


async def update_account_token(old_token: str, new_token: str, id: str) -> None:
    # Encypt tokens
    encrypted_old_token = encrypt(value=old_token)
    encrypted_new_token = encrypt(value=new_token)

    # Create update token obj
    update_token = UpdateToken(
        id=id,
        old_token=encrypted_old_token,
        new_token=encrypted_new_token
    )

    # Serialize
    update_token_event = update_token.serialize()
    
    # Emit update token event
    await produce_event(topic=settings.api_update_token, value=update_token_event)


async def invalidate_auth_token(email: EmailStr, token: str):
    # Invalidate auth token
    logger.info('Invalidating auth token')

    # Encrypt auth token
    encrypted_token = encrypt(value=token)

    # Create key
    key = f"auth_token:{email}-{encrypted_token}"
    
    # Create
    invalidate_token = InvalidateCache(key=key)

    # Serialize
    invalidate_token_event = invalidate_token.serialize()

    # Emit auth token invalidate
    logger.info('Emitting invalidate auth token event.')
    await produce_event(topic=settings.api_invalidate_cache_topic, value=invalidate_token_event)


async def invalidate_otp(email: EmailStr, otp: str, purpose: str):
    # Invalidate auth token
    logger.info('Invalidating OTP')

    # Encrypt auth token
    encrypted_otp = encrypt(value=otp)

    # Create key
    key = f"otp:{email}-{encrypted_otp}-{purpose.lower()}"
    
    # Create
    invalidate_token = InvalidateCache(key=key)

    # Serialize
    invalidate_token_event = invalidate_token.serialize()

    # Emit auth token invalidate
    logger.info('Emitting invalidate otp event.')
    await produce_event(topic=settings.api_invalidate_cache_topic, value=invalidate_token_event)
     