from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError, ExpiredSignatureError, InvalidTokenError

from app.database import get_user
from app.schemas.users import RefreshToken, Token, UserDb
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    ACCESS_TOKEN_SECRET_KEY,
    REFRESH_TOKEN_SECRET_KEY,
    create_jwt_token,
    decode_jwt_token,
    authenticate_user,
)

auth_router = APIRouter(prefix='/api/token', tags=['Token'])

def _generate_auth_tokens(user_id: int) -> Token:
    access_token = create_jwt_token(
        data={"sub": str(user_id)},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=ACCESS_TOKEN_SECRET_KEY
    )
    refresh_token = create_jwt_token(
        data={"sub": str(user_id)},
        expires_minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
        secret_key=REFRESH_TOKEN_SECRET_KEY
    )
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@auth_router.post('', response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_db: Optional[UserDb] = authenticate_user(
        email=form_data.username, password=form_data.password
    )
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )
    return _generate_auth_tokens(user_db.id)

@auth_router.post('/refresh', response_model=Token)
async def refresh_token_endpoint(token: RefreshToken):
    user_id: Optional[str] = None
    try:
        token_payload = decode_jwt_token(token.refresh_token, REFRESH_TOKEN_SECRET_KEY)
        user_id = token_payload.get('sub')
        
        if not user_id:
            raise InvalidTokenError("Token missing user ID (sub) claim.")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired. Please log in again.'
        )
    except (InvalidTokenError, PyJWTError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid refresh token: {e}'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An internal error occurred during token processing: {e}'
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid user ID format in token.'
        )

    user_db: Optional[UserDb] = get_user(user_id_int)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found or inactive.'
        )
    
    return _generate_auth_tokens(user_db.id)