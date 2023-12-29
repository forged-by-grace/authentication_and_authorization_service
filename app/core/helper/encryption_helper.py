import hashlib


def encrypt(value: str) -> str:
    # encode string
    encoded_str = value.encode()

    # Encrypt
    encrypted_str_obj = hashlib.sha3_512(encoded_str)

    
    # return the hashed_str
    return encrypted_str_obj.hexdigest()