from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, HttpUrl
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.abspath('.env'), env_file_encoding='utf-8')
    
    # API meta info
    api_name: str
    api_version: str
    api_description: str
    api_terms_of_service: str
    api_company_name: str
    api_prefix: str
    api_company_url: HttpUrl
    api_company_email: EmailStr

    # ACCOUNT API info
    api_entry_point: str
    api_port: int
    api_reload: bool
    api_host: str
    api_lifespan: str

    # Cache credentials    
    api_redis_host: str
    api_redis_port: int
    api_redis_password: str
    api_redis_decode_response: bool
    api_redis_host_local: str

    # API constants
    min_password_length: int
    password_regex: str
    max_otp_length: int

    # API model versions
    account_model_version: int

    # API secrets
    api_refresh_token_secret: str
    api_access_token_secret: str
    api_access_token_expiry: int
    api_refresh_token_expiry: int
    api_algorithm: str
    api_token_bytes: int
    api_access_token_header_key: str
    api_refresh_token_header_key: str
    api_auth_token_expiry: int
    api_token_type: str
    api_token_aud: str
    api_token_iss: str
    api_token_sub: str

    # DB credentials
    api_db_url: str

    # Streaming topics    
    api_cache_topic: str
    api_revoke_refresh_token_topic: str
    api_logout_topic: str
    api_assign_token: str
    api_add_new_device: str
    api_invalidate_account_token: str
    api_update_token: str
    api_reused_refresh_token: str
    api_invalidate_cache_topic: str

     # Event Streaming Server
    api_event_streaming_host: str
    api_event_streaming_client_id: str
    api_otp_schema_subject: str
    api_account_schema_subject: str
    api_login_for_access_token_url: str

settings = Settings()
