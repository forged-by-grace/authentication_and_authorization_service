from fastapi import HTTPException, status

# Credential error
credential_error = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': "Bearer"}
            )
