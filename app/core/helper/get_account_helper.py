from core.helper.cache_helper import get_account_from_cache
from core.helper.encryption_helper import encrypt
from core.helper.db_helper import get_account_with_id_and_refresh_token
from core.utils.init_log import logger


async def get_account_with_refresh_token(id: str, refresh_token: str):
    account_data = {}

    # Encrypt refresh token
    encrypted_refresh_token: str = encrypt(value=refresh_token)

    # Check if account is in Cache
    account_data: dict = await get_account_from_cache(id=id)
    
    if account_data is not None:
        tokens = account_data.get('tokens')        
        if tokens and (encrypted_refresh_token in tokens):
            return account_data
        return None
    else:
        account_data = await get_account_with_id_and_refresh_token(id=id, token=refresh_token)
        return account_data

