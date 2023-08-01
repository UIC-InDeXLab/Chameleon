from pydantic import BaseModel, field_serializer

from models import Gender, Race, AgeGroup


class ImageBase(BaseModel):
    filename: str
    age_group: AgeGroup
    gender: Gender
    race: Race

    @field_serializer('gender')
    def serialize_gender(self, gender: Gender, _info):
        return gender.name

    @field_serializer('race')
    def serialize_race(self, race: Race, _info):
        return race.name

    @field_serializer('age_group')
    def serialize_age_group(self, age_group: AgeGroup):
        return age_group.name


class ImageCreate(ImageBase):
    pass


class ExportImageBase(BaseModel):
    filename: str
    age_group: AgeGroup
    gender: Gender
    race: Race


class Image(ImageBase):
    id: str
    filename: str
    age_group: AgeGroup
    gender: Gender
    race: Race

    class Config:
        from_attributes = True
