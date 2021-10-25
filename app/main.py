from fastapi import FastAPI
from fastapi.params import Form
from fastapi_mail import MessageSchema

from .send_email import fast_mail


app = FastAPI(title="results-server")


@app.get(path="/", description="returns a welcome message")
def home():
    return "Welcome to Results-Server"


@app.get(path="/2")
def home2():
    return "enter credentials"

html = """
<p>Hi this test mail, thanks for using Fastapi-mail, Your OTP is 123456 </p> 
"""

@app.post(path='/auth/email', description="Authentication via E-Mail")
async def send_email(email: str = Form(..., description='email address to send OTP')):
    # send an email

    message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=[email],  # List of recipients, as many as you can pass 
            body=html,
            subtype='html'
    )
            
    await fast_mail.send_message(
        message,
        # template_name="../.templates/email/email.html"
     )
    return "ok"