from fastapi import FastAPI
from fastapi.params import Body
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from datetime import datetime, timedelta

from .utils import get_otp
from .config import settings
from .table import get_session, Student


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
)

app = FastAPI(title="Students Result Server")

MAX_ATTEMPTS = 3
OTP_EXPIRY_SECONDS = timedelta(seconds=60)
students_dict = {}

html = """
<p>Welcome to Students Results Server, Your OTP is {otp}</p> 
"""

session = get_session()

@app.post("/student/generate-otp")
async def student_email_auth(
    email: EmailStr = Body(..., description="Enter the e-mail to send OTP")
):

    student = session.query(Student).filter(Student.email==email).first()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not a registered student'
        )

    otp = get_otp()

    body = html.format(otp=otp)

    message = MessageSchema(
        subject="Students Result Server",
        recipients=[email],  # List of recipients, as many as you can pass
        body=body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    timestamp = datetime.now()
    students_dict[email] = {"otp": otp, "attempts": 0, "timestamp": timestamp}

    return JSONResponse(
        content={"message": "OTP successfully sent"}, status_code=status.HTTP_200_OK
    )


@app.post("/student/validate-otp")
def student_otp_validate(
    email: EmailStr = Body(..., description="Enter the e-mail to send OTP"),
    otp: str = Body(
        ..., min_length=6, max_length=6, description="OTP received in e-mail`"
    ),
):

    student = students_dict.get(email, None)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized email, generate otp first",
        )

    stored_otp = student.get("otp")
    attempts = student.get("attempts")
    generated_timestamp = student.get("timestamp")
    current_timestamp = datetime.now()

    print(current_timestamp - generated_timestamp)

    if (current_timestamp - generated_timestamp) > OTP_EXPIRY_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OTP expired, generate new OTP",
        )

    if attempts == MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid otp entered, Maximum number of attempts reached",
        )

    elif otp != stored_otp:
        student["attempts"] += 1
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid otp entered, number of attempts remaining are {MAX_ATTEMPTS - student['attempts']}",
        )
    elif otp == stored_otp:
        # send results
        print("results sent succesfully")
        del students_dict[email]
        return JSONResponse(
            content={"message": "results sent to email"}, status_code=status.HTTP_200_OK
        )
