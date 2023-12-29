from fastapi import HTTPException, status, Request

from core.helper.token_helper import *
from core.helper.account_helper import *
from core.helper.cache_helper import *

from core.enums.auth_enum import Role

from fastapi.responses import JSONResponse
from core.utils.init_log import logger
from core.utils.error import credential_error


async def verify_access_token_ctrl(request: Request) -> dict:
    # Access token
    logger.info('Checking if header has authorization token.')
    access_token = has_token(request=request)
    if not access_token:
        raise credential_error
    
    # Validate token
    logger.info('Verifying token')
    valid_token_data = verify_token(token=access_token, secret=settings.api_access_token_secret)
    if not valid_token_data:
        logger.error(f'Invalid access token:{access_token}')
        raise credential_error
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=valid_token_data
    )
    

async def create_access_token_ctrl(request: Request) -> dict:
    # Get refresh token
    logger.info('Checking if header has authorization token.')
    refresh_token = has_token(request=request)
    if not refresh_token:
        raise credential_error
    
    # Validate refresh token
    logger.info('Validating token.')
    token_data = verify_token(token=refresh_token, secret=settings.api_refresh_token_secret)
    
    # Check if its reused token
    logger.info('Checking if its reused token.')
    account_data = await is_reused_token(id=token_data.get('id'), token=refresh_token)
    if not account_data:
        logger.warning('Reused token detected.')
        await invalidate_account_tokens(id=token_data.get('id'))    
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reused refresh token detected.'
        )
    
    # Check if account belongs to admin
    is_admin = account_data.get('role').get('name') == Role.admin.value

    # Generate access and refresh tokens
    new_access_token, new_refresh_token = generate_token_set(
        id=account_data.get('_id'), 
        is_admin=is_admin, 
        firstname=account_data.get('firstname'), 
        lastname=account_data.get('lastname'), 
        email=account_data.get('email'))
    
    # Update token in database
    await update_account_token(
        old_token=refresh_token, 
        new_token=new_refresh_token, 
        id=account_data.get('_id'))
   
    # Create response dict
    token_response = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": settings.api_token_type,
        "expiry": settings.api_access_token_expiry
    }

    logger.info('Tokens generated successfully.')
    
    return token_response


async def login_for_access_token_ctrl(request: Request, data, auth_type: str) -> dict:    # Validate credentials
    logger.info('Validating account credentials.')
    account_data = await authenticate_account(device_ip= request.client.host, data=data, auth_type=auth_type)

    # Check if account belongs to admin
    is_admin = account_data.role.name == Role.admin.value

    # Generate access and refresh tokens
    access_token, refresh_token = generate_token_set(id=account_data.id, is_admin=is_admin, firstname=account_data.firstname, lastname=account_data.lastname, email=account_data.email)
    
    # Create response dict
    token_response = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": settings.api_token_type,
        "expiry": settings.api_access_token_expiry
    }

    # Update account
    await update_account(token=refresh_token, id=account_data.id, email=account_data.email, device_ip=request.client.host, device_data=data.device_info)

    return token_response


async def logout_ctrl(request: Request) -> None:
    # Get refresh token
    logger.info('Fetching authorization token')    
    refresh_token = has_token(request=request)
    if not refresh_token:
        raise credential_error    
    
     # Validate refresh token
    logger.info('Validating refresh token')
    token_data = verify_token(token=refresh_token, secret=settings.api_refresh_token_secret)
    if not token_data:  
       raise credential_error
   
    # Check if its reused token
    logger.info('Checking if its reused token.')
    account_data = await is_reused_token(id=token_data.get('id'), token=refresh_token)
    if not account_data:
        logger.warning('Reused token detected.')
        await invalidate_account_tokens(id=token_data.get('id'))    
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reused refresh token detected.'
        )
    
    # Revoke refresh token
    logger.info('Revoking refresh token')
    await revoke_refresh_token(id=token_data.get('id'), token=refresh_token, device_ip=request.client.host)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Logout successful."
    )


async def verify_one_time_password_ctrl(verify_otp: VerifyOTP) -> str:
    # Validate one-time-password
    logger.info('Validating OTP.')
    valid_token = await is_valid_otp(verify_otp=verify_otp)
    if not valid_token:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid one-time-password'
        )

    # Create token
    logger.info('Creating auth token.')
    auth_token = create_auth_token(bytes=settings.api_token_bytes)

    # Encrypt auth token
    encrypted_auth_token = encrypt(value=auth_token)
    
    # Cache token
    logger.info('Caching auth token.')

    # Produce a cache token event
    await cache_auth_token_event(token=encrypted_auth_token, email=verify_otp.email)
   
    # Invalidate OTP
    await invalidate_otp(otp=verify_otp.one_time_password, email=verify_otp.email, purpose=verify_otp.purpose)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'auth-token': auth_token}
    )


async def verify_auth_token_ctrl(email: EmailStr, auth_token: str):
    # Validate auth token
    logger.info('Validating auth token.')
    valid_token = await is_valid_auth_token(token=auth_token, email=email)
    if not valid_token:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Invalid auth token.'            
            )
    
    # Invalidate auth token
    await invalidate_auth_token(email=email, token=auth_token)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'msg': 'Valid auth token'}
    )


