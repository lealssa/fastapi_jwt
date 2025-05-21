from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    
class UserCreate(UserBase):    
    password: str
    password_confirmation: str
    
class User(UserBase):
    id: int
    
class UserDb(User):
    password_hash: str
    
class UserDbCreate(UserDb):
    id: int | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserPassword(BaseModel):
    old_password: str
    new_password: str
    new_password_confirmation: str    
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
class RefreshToken(BaseModel):
    refresh_token: str