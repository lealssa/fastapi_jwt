from typing import Annotated
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException, status

from app.security import oauth2_scheme, decode_jwt_token, ACCESS_TOKEN_SECRET_KEY

async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )    
    try:
        payload = decode_jwt_token(token, ACCESS_TOKEN_SECRET_KEY)
        id = payload.get("sub")
        if id is None:
            raise credentials_exception      
    except jwt.InvalidTokenError as e:
        raise credentials_exception
    return int(id)