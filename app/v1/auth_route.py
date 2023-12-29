from fastapi import APIRouter, Depends, status
from core.model.account_model import *
from core.helper.account_helper import get_current_active_account
from core.controllers.auth_controller import *
from core.enums.auth_enum import AuthType


auth = APIRouter(
    prefix=f"{settings.api_prefix}auth",
    tags=['Auth'],
)


@auth.get('/access-token/verify/', description='Verify access token', status_code=status.HTTP_200_OK, response_model=VerifyTokenResponse)
async def verify_access_token(request: Request):
    return await verify_access_token_ctrl(request=request)


@auth.get('/access-token/refresh/', description="Get a new access and refresh token pair from pre-issued refresh token.", response_model=TokenResponse)
async def get_new_access_token(request: Request):
    return await create_access_token_ctrl(request=request)


@auth.post('/login/email/', description='This endpoint returns an access token and a refresh token for an authenticated client', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_with_email_for_access_token(request: Request, data: AccountLoginWithEmail):
   return await login_for_access_token_ctrl(request=request, data=data, auth_type=AuthType.email.value)


@auth.post('/login/phone-number/', description='This endpoint returns an access token and a refresh token for an authenticated client', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_with_phone_number_for_access_token(request: Request, data: AccountLoginWithPhone):
   return await login_for_access_token_ctrl(data=data, auth_type=AuthType.phone, request=request)


@auth.post('/otp/verify/', description="Verify OTP and generate authorization token")
async def verify_one_time_password(verify_otp: VerifyOTP):
    return await verify_one_time_password_ctrl(verify_otp=verify_otp)


@auth.post('/auth-token/verify/', description="Verify authorization token")
async def verify_auth_token(verify_auth_token: VerifyAuthToken):
    return await verify_auth_token_ctrl(email=verify_auth_token.email, auth_token=verify_auth_token.auth_token)


@auth.post('/logout/', description="Logout an account")
async def logout(request: Request):
    return await logout_ctrl(request=request)
