from fastapi_mail import ConnectionConfig, FastMail

conf = ConnectionConfig(
    MAIL_USERNAME = "",
    MAIL_PASSWORD = "",
    MAIL_FROM = "",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

fast_mail = FastMail(conf)