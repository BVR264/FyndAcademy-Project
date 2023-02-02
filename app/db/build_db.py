from csv import DictReader
from pathlib import Path

from sqlalchemy.engine import create_engine

from app.db.config import db_uri, settings
from app.db.session import get_session
from app.db.tables import Base, Student


def create_tables():
    engine = create_engine(db_uri)
    engine.execute(f"CREATE DATABASE IF NOT EXISTS {settings.database_name}")
    engine.execute(f"USE {settings.database_name}")
    Base.metadata.create_all(engine)


def populate_student_table():
    # read students data from csv and insert data to sb
    data_rel_filepath = "data/student.csv"
    data_filepath = Path(__file__).absolute().parent.parent.parent / data_rel_filepath

    engine = create_engine(f"{db_uri}/{settings.database_name}", echo=True)
    session = get_session(engine)

    with open(data_filepath) as file_handler:
        reader = DictReader(file_handler)

        with engine.connect():

            for row in reader:
                student = Student(**row)
                session.add(student)

            session.commit()


# def populate_admin_table():
#     # read students data from csv and insert data to sb
#     data_rel_filepath = "data/admin.csv"
#     data_filepath = Path(__file__).absolute().parent.parent.parent / data_rel_filepath

#     engine = create_engine(f"{db_uri}/{settings.database_name}", echo=True)
#     session = get_session(engine)

#     with open(data_filepath) as file_handler:
#         reader = DictReader(file_handler)

#         with engine.connect():

#             for row in reader:
#                 admin = Admin(**row)
#                 session.add(admin)

#             session.commit()


if __name__ == "__main__":
    create_tables()
    # populate_admin_table()
    populate_student_table()
