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


class AgeGroup:
    def __init__(self, id: int, name: str, start_age: int, end_age: int):
        self.id = id
        self.name = name
        self.start_age = start_age
        self.end_age = end_age

    def __str__(self):
        return f"{self.name} is from {self.start_age} until {self.end_age}"

    def __repr__(self):
        return self.__str__()


class AgeGroupManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgeGroupManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, age_groups: list[AgeGroup]):
        if not hasattr(self, '_initialized'):
            self._age_groups = age_groups
            self._initialized = True

    @property
    def age_groups(self):
        return self._age_groups

    def get_age_group_by_age(self, age: int):
        for g in self.age_groups:
            if g.start_age <= age < g.end_age:
                return g

    def get_age_group_by_id(self, id: int):
        for g in self.age_groups:
            if g.id == id:
                return g
        return None


class AgeGroupGenderRacePattern:
    def __init__(self, string: str, manager: AgeGroupManager):
        args = list(string)
        assert len(args) == 3
        self.age_group_id = int(args[0])
        self.age_group = manager.get_age_group_by_id(self.age_group_id)
        self.gender = Gender(int(args[1]))
        self.race = Race(int(args[2]))

    @property
    def prompt(self):
        return " ".join([self.race.name, self.gender.name, self.age_group.name])


class Image(Base):
    __tablename__ = "images"

    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    filename = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(Enum(Gender))
    race = Column(Enum(Race))
