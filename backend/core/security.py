from core.config import pwd_context, sb_client
from fastapi import HTTPException
from passlib.exc import UnknownHashError

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return plain_password == hashed_password
