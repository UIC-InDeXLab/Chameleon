from sqlalchemy.orm import Session

import schemas
from models import Gender, Image, Race


def get_image_by_id(db: Session, image_id: str):
    return db.query(Image).filter(Image.id == image_id).first()


def get_image_by_file_name(db: Session, file_name: str):
    return db.query(Image).filter(Image.file_name == file_name).first()


def get_images(db: Session, skip: int = 0, limit: int = 100,
               gender: Gender = None, race: Race = None):
    filters = {k: v for k, v in (('gender', gender), ('race', race)) if v is not None}
    return db.query(Image).filter_by(**filters).offset(skip).limit(limit).all()


def get_image_by_gender(db: Session, gender: Gender, skip: int = 0, limit: int = 100):
    return db.query(Image).filter(Image.gender == gender).offset(skip).limit(limit).all()


def create_image(db: Session, image: schemas.ImageCreate):
    db_image = Image(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
