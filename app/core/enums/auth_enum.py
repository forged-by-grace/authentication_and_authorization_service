from enum import Enum

class AuthType(str, Enum):
    email='email'
    username='username'
    phone='phone'

class Role(str,Enum):
    anonymouse='anonymouse'
    authenticated='authenticated'
    admin='admin'

class OTP_Purpose(str, Enum):
     email_verification='email_verification'
     phone_verification='phone_verification'
     forgot_password='forgot_password'
     reset_password='reset_password'
     transaction_verification='transaction_verification'
     
