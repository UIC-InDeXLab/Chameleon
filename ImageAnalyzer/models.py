import uuid
from enum import IntEnum

from sqlalchemy import Column, Integer, String, Enum

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


class AgeGroup(IntEnum):
    infant = 0
    pre_schooler = 1
    school_age_child = 2
    adolescents = 3
    young_adult = 4
    adult = 5
    middle_aged_person = 6
    senior = 7
    elderly = 8


class AgeGroupGenderRacePattern:
    def __init__(self, string: str):
        args = list(string)
        assert len(args) == 3
        self.age_group = AgeGroup(int(args[0]))
        self.gender = Gender(int(args[1]))
        self.race = Race(int(args[2]))

    @property
    def prompt(self):
        return " ".join([self.race.name.replace("_", " "),
                         self.gender.name.replace("_", " "),
                         self.age_group.name.replace("_", " ")])


class Image(Base):
    __tablename__ = "images"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    filename = Column(String, unique=True, index=True)
    age_group = Column(Enum(AgeGroup))
    gender = Column(Enum(Gender))
    race = Column(Enum(Race))
