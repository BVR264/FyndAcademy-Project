from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "student"

    email = Column("email", String(320), primary_key=True)
    name = Column("name", String(320))
    english = Column("english", Integer)
    maths = Column("maths", Integer)
    science = Column("science", Integer)


# class Admin(Base):
#     __tablename__ = "admin"

#     email = Column("email", String(320), primary_key=True)
#     name = Column("name", String(320))
