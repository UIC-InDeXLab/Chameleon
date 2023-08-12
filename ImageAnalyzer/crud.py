from sqlalchemy import func
from sqlalchemy.orm import Session

import schemas
from models import Gender, Image, Race, AgeGroup


def get_images(db: Session, skip: int = 0, limit: int = None,
               gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
               order_by=None):
    filters = {k: v for k, v in (('gender', gender), ('race', race), ('age_group', age_group)) if v is not None}
    q = db.query(Image).filter_by(**filters)
    if order_by is not None:
        q = q.order_by(order_by)
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def get_random_images(db: Session, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                      limit: int = None):
    return get_images(db=db, gender=gender, race=race, age_group=age_group, order_by=func.random(), limit=limit)


def create_image_by_filename(db: Session, filename: str):
    args = filename.split("_")
    age_group: AgeGroup = AgeGroup(int(args[0]))
    gender: Gender = Gender(int(args[1]))
    race: Race = Race(int(args[2]))
    image = schemas.ImageCreate(age_group=age_group, gender=gender, race=race, filename=filename, is_generated=False)
    return create_image(db=db, image=image)


def create_image(db: Session, image: schemas.ImageCreate):
    db_image = Image(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_table_df(db: Session):
    return [schemas.ExportImageBase.model_construct(
        filename=r.filename, age_group=r.age_group, gender=r.gender, race=r.race, is_generated=r.is_generated)
        for r in
        db.query(Image).all()]


def get_partial_table_df(db: Session, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                         limit: int = 1):
    return [schemas.ExportImageBase.model_construct(
        filename=r.filename, age_group=r.age_group, gender=r.gender, race=r.race, is_generated=r.is_generated)
        for r in
        get_random_images(db=db, gender=gender, race=race, age_group=age_group, limit=limit)]
