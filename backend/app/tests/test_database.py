from sqlmodel import Field, SQLModel, create_engine
from app.core.config import settings


def test_postgres_database():
    class Hero(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        name: str
        secret_name: str
        age: int | None = None

    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    SQLModel.metadata.create_all(engine)
