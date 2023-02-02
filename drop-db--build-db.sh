export DATABASE_USER=vijay
export DATABASE_PASSWORD=HelloWorld123#
export DATABASE_SERVER=localhost
export DATABASE_NAME=result_server
# builds the database from csv
python -m app.db.drop_db
python -m app.db.build_db