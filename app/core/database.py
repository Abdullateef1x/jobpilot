from sqlmodel import Session, SQLModel, create_engine

from app.config import setting

# Setup the database engine

def  get_engine():
    url = setting.DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return create_engine(url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(get_engine())   # type: ignore[attr-defined]


def get_session():
    with Session(get_engine()) as session:
        yield session