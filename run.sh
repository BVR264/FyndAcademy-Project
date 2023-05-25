export DATABASE_USER=vijay
export DATABASE_PASSWORD=HelloWorld123#
export DATABASE_SERVER=localhost
export DATABASE_NAME=result_server
export MAIL_USERNAME=vijaybomma0106@gmail.com
export MAIL_PASSWORD=yqgfajbztvwqmnyv 
export MAIL_FROM=vijaybomma0106@gmail.com
export MAX_ATTEMPTS=3
export OTP_EXPIRY_SECONDS=60
export PORT=8000
export SECRET_PIN=secretpinn
# run the server
uvicorn "app.main:app" --host=0.0.0.0 --port=$PORT
