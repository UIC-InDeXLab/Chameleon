import uuid
from enum import IntEnum

from sqlalchemy import Column, String, Enum, Boolean

from database import Base
from singleton import Singleton


class Attribute:
    def __init__(self, name: str, cardinality: int, ordered: bool, position: int, column_number: int, mapping: dict):
        self.column_number = column_number
        self.name = name
        self.cardinality = cardinality
        self.ordered = ordered
        self.mapping = mapping
        self.position = position


class Dataset:
    def __init__(self, name, resource_path, csv_path, attributes):
        self.name = name
        self.__resource_path__ = resource_path
        self.__csv_path__ = csv_path
        self.attributes = [Attribute(**a) for a in attributes]

    def get_attribute_by_name(self, name):
        for a in self.attributes:
            if a.name == name:
                return a
        return None

    def get_attribute_by_column_number(self, col_name):
        for a in self.attributes:
            if a.column_number == col_name:
                return a
        return None

    def get_prompt(self, filters: dict):
        atts = []
        for k, v in filters.items():
            a = self.get_attribute_by_name(k)
            atts.append((a.position, a.mapping.get(str(v))))

        atts = sorted(atts, key=lambda x: x[0])
        return " ".join([a[1] for a in atts])

    @property
    def num_attributes(self):
        return len(self.attributes)

    @property
    def cardinality_of_attributes(self):
        return [a.cardinality for a in self.attributes]

    @property
    def attributes_ids(self):
        return [a.column_number for a in self.attributes]


@Singleton
class DatasetManager:
    def __init__(self):
        self.datasets = []

    def add_dataset(self, ds: Dataset):
        self.datasets.append(ds)

    def get_dataset(self) -> Dataset:
        return self.datasets[0]


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
    elderly = 7


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
