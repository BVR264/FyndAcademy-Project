from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from csv import DictReader
from pathlib import Path

# declare db creation details
user = "vijay"
password = "HelloWorld123#"
server = "localhost"
database = "students_results3"
db_uri =  f"mysql+mysqlconnector://{user}:{password}@{server}"

engine = create_engine(db_uri, echo=True)
engine.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
engine.execute(f"USE {database}")

Base = declarative_base()

class Student(Base):
   __tablename__ = 'student'

   email = Column("email", String(320), primary_key=True)
   marks = Column("marks", Integer, nullable=False)

Base.metadata.create_all(engine)

# read students data from csv and insert data to sb
students_results_rel_filepath = 'data/students-results.csv'
students_results_filepath = Path(__file__).absolute().parent.parent / students_results_rel_filepath

engine = create_engine(f"{db_uri}/{database}", echo=True)
DatabaseSession = sessionmaker(bind=engine)
db_session = DatabaseSession()

with open(students_results_filepath) as file_handler:
   reader = DictReader(file_handler)

   with engine.connect() as conn:

      for row in reader:
         student = Student(email=row['email'], marks=row['marks'])
         db_session.add(student)

      db_session.commit()
