from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.user import User, UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    hashed = hash_password(user_in.password)

    db_user = User (
        email = user_in.email,
        password_hash = hashed,
        name=user_in.name,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    
def get_user_by_uuid(db: Session, user_id) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    return db.exec(statement).first()


def update_user_resume(db, user, key, parsed_data):

    user.current_resume_key = key
    user.parsed_resume_data = parsed_data

    db.commit()
    db.refresh(user)