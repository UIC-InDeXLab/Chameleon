import uuid
from enum import IntEnum

from sqlalchemy import Column, String, Enum, Boolean

from database import Base


class Gender(IntEnum):
    male = 0
    female = 1


class Race(IntEnum):
    white = 0
    black = 1
    asian = 2
    indian = 3


class AgeGroup(IntEnum):
    infant = 0
    preschooler = 1
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
        self.age_group = AgeGroup(int(args[0])) if args[0] != "x" else None
        self.gender = Gender(int(args[1])) if args[1] != "x" else None
        self.race = Race(int(args[2])) if args[2] != "x" else None

    @property
    def prompt(self):
        not_none_attributes = [i for i in [self.race, self.gender, self.age_group] if i is not None]
        return " ".join([i.name.replace("_", " ") for i in not_none_attributes])


class Image(Base):
    __tablename__ = "images"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    filename = Column(String, unique=True, index=True)
    age_group = Column(Enum(AgeGroup))
    gender = Column(Enum(Gender))
    race = Column(Enum(Race))
    is_generated = Column(Boolean, default=False)
