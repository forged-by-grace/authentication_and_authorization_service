from passlib.hash import bcrypt as pwd_context
from core.utils.init_log import logger


def verify_password(plain_password, hashed_password):
   try:
        return  pwd_context.verify(secret=plain_password, hash=hashed_password)
   except Exception as err:
       logger.error(f"Failed to verify password due to error: {str(err)}")
     