from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import EmailStr, Field, SecretStr
from datetime import datetime
from core.model.device_model import Device
from core.model.role_model import *

from typing import Optional, List

    
class AccountInDB(AvroBaseModel):
    id: str = Field(description="A unique string representing the account id",
                    json_schema_extra={'id': '7845941214687'}, alias='_id')
    email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])
    firstname: str = Field(description="A string. This is the user's first name.",
                           examples=['John'])
    lastname: str = Field(description="A string. This is the user's lastname.",
                          examples=['Doe'])
    phone_number: str = Field(description="A string. This is the user's mobile or contact number. This will be validated before use.",
                              examples=['915 1234 789'])
    country_code: str = Field(description="A string. This is the user's country code.",
                              examples=['+234'])
    country: str = Field(description="A string. This is the user's country of residence. e.g. Nigeria", 
                         examples=['Nigeria'])
    username: Optional[str] = Field('ID used to retrieve the account username')
    display_pics: Optional[str] = Field(description='Account display image',)
    hashed_password: str = Field(exclude=True, description='Account password hashed')
    version: int = Field(exclude=True, description="A string. This represents the version of database schema")
    disabled: bool = Field(default=True, 
                           description="A boolean. This is used to disable a user's account")
    email_verified: bool = Field(default=False, 
                                 description="A boolean used to check the verification state of the account's email")
    phone_verified: bool = Field(default=False, 
                                 description="A boolean used to check the verification state of the user's phone number")
    is_active: bool = Field(default=False, description="A boolean used to verify the login state of the account")
    active_device_count: int = Field(exclude=True, description='An integer representing the number of active devices connecting to a single account')
    active_devices: List[str] = Field(exclude=True, description='A list showing all active account devices')
    role: Role = Field(description='Account role')
    created_on: datetime = Field(exclude=True, description='Timestamp used to track account creation date.')


class LoginPassword(AvroBaseModel):    
    password: str = Field(description='A secret string representing the account password')
    device_info: Device = Field(description='Device data')


class AccountLoginWithEmail(LoginPassword):
    email: EmailStr = Field(description='An email str used to create an account')


class AccountLoginWithPhone(LoginPassword):
    phone_number: Optional[str] = Field(description='A string representing a verified account phone number')
    

class Logout(AvroBaseModel):
    email: EmailStr = Field(description='An email string used to identify an account')
    refresh_token: str = Field(description='A string representing the refresh token.')

   
