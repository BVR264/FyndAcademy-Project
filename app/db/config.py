from pydantic import BaseSettings


class Settings(BaseSettings):
    database_user: str
    database_password: str
    database_server: str
    database_name: str


settings = Settings()  # type: ignore

db_uri = f"mysql+mysqlconnector://{settings.database_user}:{settings.database_password}@{settings.database_server}"
