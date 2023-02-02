from sqlalchemy.engine import create_engine

from app.db.config import db_uri, settings


def drop_database():
    engine = create_engine(db_uri)
    engine.execute(f"DROP DATABASE IF EXISTS {settings.database_name}")


if __name__ == "__main__":
    # drop_student_table()
    # drop_admin_table()
    drop_database()
