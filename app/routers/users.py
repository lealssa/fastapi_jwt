from typing import Optional
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.schemas.users import User, UserCreate, UserPassword, UserDbCreate
from app.security import get_password_hash, authenticate_user, verify_password
from app.dependencies import get_current_user_id

from app.database import (
    get_all_users,
    get_user,
    get_user_by_email,
    create_user,
    delete_user,
    update_user,
)

user_router = APIRouter(prefix='/api/users', tags=['Users'])

@user_router.get('', response_model=list[User])
def get_users(current_user_id: int = Depends(get_current_user_id)):
    return get_all_users()

@user_router.get('/{user_id}', response_model=User)
def get_user_by_id(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found with id {user_id}'
        )
    return user

@user_router.post('', response_model=User, status_code=status.HTTP_201_CREATED)
def add_user(user_create: UserCreate):
    user_exists = get_user_by_email(user_create.email)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User with email {user_create.email} already exists'
        )
    
    if user_create.password != user_create.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Passwords do not match'
        )
    
    password_hash = get_password_hash(user_create.password)
    
    user_db_create_data = user_create.model_dump(exclude={'password', 'password_confirmation'})
    user_db_create_data['password_hash'] = password_hash
    user_db_create = UserDbCreate(**user_db_create_data)
    
    return create_user(user_db_create)

@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found with id {user_id}'
        )
    
    if not delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to delete user with id {user_id}'
        )

@user_router.post('/me/password', status_code=status.HTTP_204_NO_CONTENT)
def change_password(user_password: UserPassword, current_user_id: int = Depends(get_current_user_id)):
    if user_password.new_password != user_password.new_password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='New passwords do not match'
        )
    
    current_user: Optional[User] = get_user(current_user_id)
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Authentication required or user not found.'
        )
    
    if not verify_password(user_password.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid current password'
        )
    
    current_user.password_hash = get_password_hash(user_password.new_password)
    
    # Assumindo que update_user sabe como lidar com a atualização do objeto User
    update_user(current_user_id, current_user)