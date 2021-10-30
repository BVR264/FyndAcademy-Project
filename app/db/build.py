from sqlalchemy.engine import create_engine
from pathlib import Path
from csv import DictReader

from app.db.session import get_session
from app.db.table import Base, Student
from app.db.config import settings, db_uri


def build_db():
    engine = create_engine(db_uri)
    engine.execute(f"CREATE DATABASE IF NOT EXISTS {settings.database_name}")
    engine.execute(f"USE {settings.database_name}")

    Base.metadata.create_all(engine)

    # read students data from csv and insert data to sb
    students_results_rel_filepath = "data/students-results.csv"
    students_results_filepath = (
        Path(__file__).absolute().parent.parent.parent / students_results_rel_filepath
    )

    engine = create_engine(f"{db_uri}/{settings.database_name}", echo=True)
    session = get_session(engine)

    with open(students_results_filepath) as file_handler:
        reader = DictReader(file_handler)

        with engine.connect() as conn:

            for row in reader:
                student = Student(**row)
                session.add(student)

            session.commit()


if __name__ == "__main__":
    build_db()
