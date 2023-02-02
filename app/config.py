from pydantic import BaseSettings


class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    TEMP_DIR: str = ".temp"
    MAX_ATTEMPTS: int = 3
    OTP_EXPIRY_SECONDS: int = 60


settings = Settings()  # type: ignore
