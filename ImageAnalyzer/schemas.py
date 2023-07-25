from pydantic import BaseModel, field_serializer

from models import Gender, Race


class ImageBase(BaseModel):
    filename: str
    age: int
    gender: Gender
    race: Race

    @field_serializer('gender')
    def serialize_gender(self, gender: Gender, _info):
        return gender.name

    @field_serializer('race')
    def serialize_race(self, race: Race, _info):
        return race.name


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: str
    filename: str
    age: int
    gender: Gender
    race: Race

    class Config:
        from_attributes = True
