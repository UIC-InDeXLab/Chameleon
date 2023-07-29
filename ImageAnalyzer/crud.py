from sqlalchemy.orm import Session
from sqlalchemy import func, between

import schemas
from models import Gender, Image, Race, AgeGroupManager


def get_image_by_id(db: Session, image_id: str):
    return db.query(Image).filter(Image.id == image_id).first()


def get_image_by_file_name(db: Session, file_name: str):
    return db.query(Image).filter(Image.filename == file_name).first()


def get_images(db: Session, skip: int = 0, limit: int = None,
               gender: Gender = None, race: Race = None, min_age: int = 0, max_age: int = 200):
    filters = {k: v for k, v in (('gender', gender), ('race', race)) if v is not None}
    q = db.query(Image) \
        .filter_by(**filters) \
        .filter(between(Image.age, min_age, max_age - 1)) \
        .order_by(Image.age) \
        .offset(skip)
    if limit:
        q = q.limit(limit)
    return q.all()


def get_image_by_gender(db: Session, gender: Gender, skip: int = 0, limit: int = 100):
    return db.query(Image).filter(Image.gender == gender).offset(skip).limit(limit).all()


def create_image_by_filename(db: Session, filename: str):
    args = filename.split("_")
    age = int(args[0])
    gender: Gender = Gender(int(args[1]))
    race: Race = Race(int(args[2]))
    image = schemas.ImageCreate(age=age, gender=gender, race=race, filename=filename)
    return create_image(db=db, image=image)


def create_image(db: Session, image: schemas.ImageCreate):
    db_image = Image(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_table_df(db: Session, manager: AgeGroupManager):
    return [schemas.ExportImageBase.model_construct(
        filename=r.filename, age=manager.get_age_group_by_age(r.age).id, gender=r.gender, race=r.race)
        for r in
        db.query(Image).all() if r.race != 4]
