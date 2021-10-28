import os
from fastapi import FastAPI
from fastapi.params import Form
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import EmailStr
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from datetime import datetime, timedelta

from . import utils, pdf
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


students_dict = {}


session = get_session()

app = FastAPI(title="Students Result Server")


@app.on_event("startup")
def create_temp_dir():
    os.makedirs(settings.TEMP_DIR, exist_ok=True)


@app.get("/student/results")
async def results():
    content = """
    <!DOCTYPE html>
    <html>
    <body>

    <h2> Students Results Server</h2>

    <form action="/student/generate-otp" method="post">
    <label for="email">E-Mail:</label><br>
    <input type="text" id="email" name="email" value="user@example.com"><br>
    <input type="submit" value="Submit">
    </form> 

    </body>
    </html>
    """

    return HTMLResponse(content=content, status_code=status.HTTP_200_OK)


# -----------------------------OTP Generation -----------------------

otp_html = """
<p>Welcome to Students Results Server, Your OTP is {otp}</p> 
"""


@app.post("/student/generate-otp")
async def student_email_auth(
    email: EmailStr = Form(..., description="Enter the e-mail to send OTP")
):

    student = session.query(Student).filter(Student.email == email).first()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a registered student",
        )

    otp = utils.generate_otp()

    body = otp_html.format(otp=otp)

    message = MessageSchema(
        subject="Students Result Server",
        recipients=[email],  # List of recipients, as many as you can pass
        body=otp_html.format(otp=otp),
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    columns = []
    values = []

    for c in student.__table__.columns:
        columns.append(c.key)
        values.append(getattr(student, c.key))

    students_dict[email] = {
        "otp": otp,
        "attempts": 0,
        "timestamp": datetime.now(),
        "columns": columns,
        "values": values,
    }

    content = f"""
    <!DOCTYPE html>
    <html>
    <body>

    <h2> Students Results Server</h2>

    <form action="/student/validate-otp" method="post">
    <label for="email">E-Mail:</label><br>
    <input type="text" id="email" name="email" value="{email}"><br>
    <label for="otp">OTP:</label><br>
    <input type="text" id="otp" name="otp"><br>
    <input type="submit" value="Submit">
    </form> 

    </body>
    </html>
    """

    return HTMLResponse(content=content, status_code=status.HTTP_200_OK)



# ------------------------- OTP Validation ----------------------------------------------

results_html = """
<h2>Hi, your result is here</h2>
"""


@app.post("/student/validate-otp")
async def student_otp_validate(
    email: EmailStr = Form(..., description="Enter the e-mail to send OTP"),
    otp: str = Form(
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

    if (current_timestamp - generated_timestamp) > timedelta(
        seconds=settings.OTP_EXPIRY_SECONDS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OTP expired, generate new OTP",
        )

    if attempts == settings.MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid otp entered, Maximum number of attempts reached",
        )

    elif otp != stored_otp:
        student["attempts"] += 1
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid otp entered, number of attempts remaining are {settings.MAX_ATTEMPTS - student['attempts']}",
        )
    elif otp == stored_otp:

        columns = student.get("columns")
        values = student.get("values")

        filename = utils.generate_random_filename(ext=".html")
        html_filepath = os.path.join(settings.TEMP_DIR, filename)
        pdf_filepath = pdf.generate_pdf(html_filepath, columns, values)

        message = MessageSchema(
            subject="Students Result Server",
            recipients=[email],
            attachments=[pdf_filepath],
            body=results_html,
            subtype="html",
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        os.remove(html_filepath)
        os.remove(pdf_filepath)

        return JSONResponse(
            content={"message": "results sent to email"}, status_code=status.HTTP_200_OK
        )
