import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Union

from fastapi import FastAPI, status, Depends
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.params import Form, Path
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from sqlalchemy.engine import create_engine

from app import pdf, utils
from app.config import settings
from app.db.config import db_uri
from app.db.config import settings as db_settings
from app.db.session import get_session
from app.db.tables import Student
from app.mail import conf

engine = create_engine(f"{db_uri}/{db_settings.database_name}", echo=True)
session = get_session(engine)

app = FastAPI(title="Result Server")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def create_temp_dir():
    os.makedirs(settings.TEMP_DIR, exist_ok=True)


# ------------------------------------------------------------------


    

@app.get("/")
@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request},
        status_code=status.HTTP_200_OK,
    )


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(
        name="about.html",
        context={"request": request},
        status_code=status.HTTP_200_OK,
    )


class Users(str, Enum):
    STUDENT = "student"


@app.get("/user/{user}")
async def email_form(request: Request, user: Users):
    return templates.TemplateResponse(
        name="email-form.html",
        context={"request": request, "user": user.value},
        status_code=status.HTTP_200_OK,
    )


# ----------------------------- OTP Generation -----------------------
current_users = {}


@app.post("/user/{user}/generate-otp")
async def _generate_otp(
    background_tasks: BackgroundTasks,
    request: Request,
    user: Users,
    email: str = Form(..., description="Enter the e-mail to send OTP"),  # type: ignore
):

    if user == Users.STUDENT:
        user_info = session.query(Student).filter(Student.email == email).first()
    # else:
    #     user_info = session.query(Admin).filter(Admin.email == email).first()

    if user_info is None:
        return templates.TemplateResponse(
            name="invalid-email.html",
            context={"request": request, "email": email, "user" : user.value},
            status_code=status.HTTP_404_NOT_FOUND
            ,
        )

    # generate otp if student exists
    otp = utils.generate_otp()
    # retrieves the values from columns of a particular user
    info = {
        column.key: getattr(user_info, column.key)
        for column in user_info.__table__.columns
    }

    current_users[email] = {
        "otp": otp,
        "attempts": 0,
        "info": info,
        "timestamp": None,
    }
    # ----------------------------
    body = f"""
    Hi, 
    
    Your OTP is {otp} 
    """

    message = MessageSchema(
        subject="Result Server",
        recipients=[email],  # type: ignore
        body=body,
        subtype=MessageType.plain,
    )

    async def send_otp_and_add_timestamp():
        await FastMail(conf).send_message(message)
        current_users[email].update(timestamp=datetime.now())

    # send the otp to email
    background_tasks.add_task(send_otp_and_add_timestamp)

    return templates.TemplateResponse(
        name="otp-form.html",
        context={"request": request, "email": email, "user": user.value},
        status_code=status.HTTP_200_OK,
        background=background_tasks,
    )


# ------------------------- OTP Validation ----------------------------------------------


@app.post("/user/{user}/validate-otp")
async def student_validate_otp(
    background_tasks: BackgroundTasks,
    request: Request,
    user: Users,
    email: str = Form(..., description="Enter the e-mail to send OTP"),  # type: ignore
    otp: str = Form(
        ..., min_length=6, max_length=6, description="OTP received in e-mail`"
    ),  # type: ignore
):

    current_user = current_users.get(email, None)
    if current_user is None:
        return templates.TemplateResponse(
            name="otp-expired-max-attempts-reached.html",
            context={
                "request": request,
                "email": email,
                "generate_otp_first": True,
                "user": user.value,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # increment attempts
    current_user["attempts"] += 1
    current_timestamp = datetime.now()

    # case 1: OTP expired
    if (current_timestamp - current_user["timestamp"]) > timedelta(
        seconds=settings.OTP_EXPIRY_SECONDS
    ):
        return templates.TemplateResponse(
            name="otp-expired-max-attempts-reached.html",
            context={
                "request": request,
                "email": email,
                "otp_expired": True,
                "user": user.value,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # case 2: OTP max attempts reached
    if current_user["attempts"] == settings.MAX_ATTEMPTS:

        return templates.TemplateResponse(
            name="otp-expired-max-attempts-reached.html",
            context={
                "request": request,
                "email": email,
                "max_attempts_reached": True,
                "user": user.value,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # case 3: incorrect OTP
    if otp != current_user["otp"]:

        return templates.TemplateResponse(
            name="incorrect-otp-form.html",
            context={
                "request": request,
                "email": email,
                "remaining_attempts": settings.MAX_ATTEMPTS - current_user["attempts"],
                "user": user.value,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # case 4: correct OTP
    elif otp == current_user["otp"]:
        if user == Users.STUDENT:

            info = current_user["info"]
            columns = list(info.keys())
            values = list(info.values())

            # generate html & pdf files
            html_filename = f"{info['name'].title()}-result.html"
            html_filepath = os.path.join(settings.TEMP_DIR, html_filename)
            pdf_filepath = pdf.generate_pdf(html_filepath, columns, values)

            results_html = f"""
            Hi {info['name'].title()}, Your result is here.
            """

            message = MessageSchema(
                subject="Result Server",
                recipients=[email],  # type: ignore
                attachments=[pdf_filepath],
                body=results_html,
                subtype=MessageType.plain,
            )

            async def send_result_and_cleanup():
                await FastMail(conf).send_message(message)
                os.remove(html_filepath)
                os.remove(pdf_filepath)
                del current_users[email]

            background_tasks.add_task(send_result_and_cleanup)

        return templates.TemplateResponse(
            name="result-sent.html",
            context={"request": request, "email": email},
            status_code=status.HTTP_200_OK,
            background=background_tasks,
        )


from pydantic import BaseModel, EmailStr, Field


class StudentValidator(BaseModel):
    email: EmailStr
    name: str
    english: int = Field(..., gt=0, le=100)
    maths: int = Field(..., gt=0, le=100)
    science: int = Field(..., gt=0, le=100)

def check_pin(pin: str):
    secret_pin = os.getenv("SECRET_PIN")  # Retrieve the PIN value from an environment variable
    if pin != secret_pin:
        raise HTTPException(status_code=400, detail="Incorrect PIN")
    return True



@app.post("/user/student/create")
def add_student(student: StudentValidator, pin: str = Depends(check_pin)):
    session.add(Student(**student.dict()))
    session.commit()
    return Response(content="created", status_code=status.HTTP_201_CREATED)
    


@app.post("/user/student/read")
def _read_student(email: EmailStr):

    student_row = session.query(Student).filter(Student.email == email).first()
    # import pdb; pdb.set_trace()

    if student_row is None:
        return Response(content="not found", status_code=status.HTTP_404_NOT_FOUND)
    else:
        info = {
            column.key: getattr(student_row, column.key)
            for column in student_row.__table__.columns
        }
        return JSONResponse(content=info, status_code=status.HTTP_200_OK)


@app.post("/user/student/delete")
def _delete_student(email: EmailStr, pin: str = Depends(check_pin)):

    student_row = session.query(Student).filter(Student.email == email)
    
    if student_row.first() is None:
        return Response(content="not found", status_code=status.HTTP_404_NOT_FOUND)
    else:
        student_row.delete()
        session.commit()
        return Response(content="deleted", status_code=status.HTTP_201_CREATED)


@app.post("/user/student/update")
def _update_student(student: StudentValidator,pin: str = Depends(check_pin)):

    student_row = session.query(Student).filter(Student.email == student.email)

    if student_row.first() is None:
        return Response(content="not found", status_code=status.HTTP_404_NOT_FOUND)

    else:
        student_row.update(student.dict())
        session.commit()
        return Response(content="updated", status_code=status.HTTP_201_CREATED)
