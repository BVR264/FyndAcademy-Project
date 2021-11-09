import os
from fastapi import FastAPI
from fastapi.params import Form
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import EmailStr
from fastapi_mail import MessageSchema, FastMail
from datetime import datetime, timedelta
from sqlalchemy.engine import create_engine

from app import utils, pdf
from app.mail import conf
from app.config import settings
from app.db.config import db_uri, settings as db_settings
from app.db.table import Student
from app.db.session import get_session


engine = create_engine(f"{db_uri}/{db_settings.database_name}", echo=True)
session = get_session(engine)

app = FastAPI(title="Students Result Server")
students_dict = {}


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


@app.post("/student/generate-otp")
async def student_generate_otp(
    email: EmailStr = Form(..., description="Enter the e-mail to send OTP")
):
    # check whether the student exists in the database
    student = session.query(Student).filter(Student.email == email).first()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not a registered student",
        )

    # generate otp if student exists
    otp = utils.generate_otp()

    body = f"""
    Welcome to Students Results Server,
    
    Your OTP is {otp} 
    """

    message = MessageSchema(
        subject="Students Result Server",
        recipients=[email],  # List of recipients, as many as you can pass
        body=body,
        subtype="html",
    )

    # send the otp to email
    fm = FastMail(conf)
    await fm.send_message(message)

    # store the student details in a dictionary
    columns = []  # used to store column names
    values = []  # used to store column values

    # retrieves the values from columns of a particular student
    for column in student.__table__.columns:
        columns.append(column.key)
        values.append(getattr(student, column.key))

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
Hi, Your result is here
"""


@app.post("/student/validate-otp")
async def student_validate_otp(
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"OTP expired, Generate new OTP",
        )

    if attempts == settings.MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid otp entered, Maximum number of attempts reached, Generate new OTP",
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

        # generate html & pdf files
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

        del students_dict[email]

        return JSONResponse(
            content={"message": "results sent to email"}, status_code=status.HTTP_200_OK
        )
