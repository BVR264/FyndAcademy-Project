from sqlalchemy import Table, String, Column, Integer, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

user = "vijay"
password = "HelloWorld123#"
server = "localhost"
database = "students_results3"
db_uri =  f"mysql+mysqlconnector://{user}:{password}@{server}/{database}"

Base = declarative_base()

class Student(Base):
   __tablename__ = 'student'

   email = Column("email", String(320), primary_key=True)
   marks = Column("marks", Integer, nullable=False)

def get_session():
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
