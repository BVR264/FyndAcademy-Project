from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


def get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
