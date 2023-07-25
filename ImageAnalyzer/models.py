import uuid

from sqlalchemy import Column, Integer, String, Enum
from enum import IntEnum
from database import Base


class Gender(IntEnum):
    male = 0
    female = 1


class Race(IntEnum):
    white = 0
    black = 1
    asian = 2
    indian = 3
    other = 4


class Image(Base):
    __tablename__ = "images"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    filename = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(Enum(Gender))
    race = Column(Enum(Race))
