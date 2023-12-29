from core.connection.db_connection import account_col

from core.model.account_model import AccountInDB

from pydantic import EmailStr

from core.helper.encryption_helper import encrypt

from core.utils.init_log import logger


async def get_account_by_email(email: EmailStr):
    """    
    This is used to retrieve an account from the database using email.
    @params {email} - The email registered to the account to be retrieved.
    @returns {object} - A dict containing the account data
    
    """
    
    # Filter
    filter = {"email": email}

    # Query
    response = await account_col.find_one(filter=filter)

    # Check if response is None
    if not response:
        return None
    
    # Deserialize
    account_obj = AccountInDB(**response)

    return account_obj


async def get_account_by_id(id: str):
    """
    This is used to retrieve accounts from the database using the id.
    @params {id} - The id registered to the account.
    @returns {object} - A dict containing the account data
    """

    # Filter
    filter = {"_id": id}

    # Query
    response = await account_col.find_one(filter=filter)

    # Check if response is None
    if not response:
        return None
    
    # Deserialize
    account_obj = AccountInDB(**response)

    return account_obj


async def get_account_by_phone_number(phone_number: str):
    """
    This is used to retrieve accounts from the database using the id.
    @params {phone_number} - The phone number registered to the account.
    @returns {object} - A dict containing the account data
    """
    
    # Filter
    filter = {"phone_number": phone_number}

    # Query
    response = await account_col.find_one(filter=filter)

    # Check if response is None
    if not response:
        return None
    
    # Deserialize
    account_obj = AccountInDB(**response)

    return account_obj


async def get_account_with_id_and_refresh_token(id: str, token: str):
    logger.info(f"Fetching account:{id} from database.")
    
    # Encrypt token
    encrypted_token = encrypt(token)

    # Filter
    filter = {
        '$and': [
            {'_id': id}, 
            {'tokens': {'$in': [encrypted_token]}}
        ]
    }

    # Query
    response = await account_col.find_one(filter=filter)

    return response


