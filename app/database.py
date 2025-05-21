from app.schemas.users import UserDb, UserDbCreate
from typing import Dict, Optional, Any

fake_user_db: Dict[int, UserDb] = {}

_user_id_sequence: int = 0

def generate_user_id() -> int:
    global _user_id_sequence
    _user_id_sequence += 1
    return _user_id_sequence

def get_all_users() -> list[UserDb]:
    return list(fake_user_db.values())

def get_user(user_id: int) -> Optional[UserDb]:
    return fake_user_db.get(user_id)

def get_user_by_email(email: str) -> Optional[UserDb]:
    return next((u for u in fake_user_db.values() if u.email == email), None)

def create_user(user_data: UserDbCreate) -> UserDb:
    new_user_id = generate_user_id()
    user_db_instance = UserDb(id=new_user_id, **user_data.model_dump(exclude_none=True))
    fake_user_db[new_user_id] = user_db_instance
    return user_db_instance

def update_user(id: int, user_updated: UserDb):
    fake_user_db[id] = user_updated

def delete_user(user_id: int) -> bool:
    if user_id in fake_user_db:
        del fake_user_db[user_id]
        return True
    return False
