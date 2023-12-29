from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from dataclasses_avroschema.pydantic import AvroBaseModel
from typing import Literal
from core.enums.auth_enum import OTP_Purpose
from core.model.device_model import Device


class Token(BaseModel):
    access_token: str = Field(description='A string representing an access token')
    token_type: str = Field(description='A string representing the token type')
    expiry: int = Field(default=datetime.utcnow(), description='A datetime representing the expiry datetime of the access token')


class TokenResponse(Token):
    refresh_token: str = Field(description='A string representing an access token')


class VerifyOTP(BaseModel):
    email: EmailStr = Field(index=True, description='An email string representing the account email')
    one_time_password: str = Field(index=True, description='A string representing the one-time-password')
    purpose: str = Field(description='The purpose of the otp')


class VerifyOTPCache(BaseModel):
    email: EmailStr = Field(index=True, description='An email string representing the account email')
    one_time_password: str = Field(index=True, description='A string representing the one-time-password')


class VerifyAuthToken(BaseModel):
    email: EmailStr = Field(description='An email string used to identify an account')
    auth_token: str = Field(description='A string representing the authorization token')


class RevokeRefreshToken(AvroBaseModel):
    id: str = Field(description='A string used to identify an account')
    token: str = Field(description='A string representing the refresh token.')
    device_ip: str = Field(description='A string representing the IP address of the current device.')


class AuthToken(AvroBaseModel):
    email: EmailStr = Field(description='An email string used to identify an account')
    token: str = Field(description='Auth token used to authorize account changes.') 
    expiry: datetime = Field(description='Expiry tracks the validity of the auth token')


class AssignToken(AvroBaseModel):
    id: str = Field(description='Used to identify the account')
    email: EmailStr = Field(description="Used to identify the account.")
    device_ip: str = Field(description='Used to track the device IP address')
    token: str = Field(description='Encrypted refresh token')
    device_info: Device = Field(description='Device meta data.')

class ReusedToken(AvroBaseModel):
    id: str = Field(description='Used to identify the account')


class UpdateToken(AvroBaseModel):
    id: str = Field(description='Used to identify the account')
    old_token: str = Field(description='Encrypted old refresh token')
    new_token: str = Field(description='Encrypted new refresh token')


class VerifyTokenResponse(AvroBaseModel):
    iss: str = Field(description='Company issueing the token')
    aud: str = Field(description='The clients')
    sub: str = Field(description='The subject of the token')
    firstname: str = Field(description='The firstname of the client.')
    lastname: str  = Field(description='The lastname of the client.')
    email: EmailStr = Field(description='Email of the client.')
    id: str = Field(description='Unique client ID')
    admin: bool = Field(description='Checks if client is an admin')
    iat: datetime = Field(description='Timestamp token was issued')
    exp: datetime = Field(description='Token expiration timestamp')
    