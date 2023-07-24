from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/v1/images/", response_model=schemas.Image)
def create_user(image: schemas.ImageCreate, db: Session = Depends(get_db)):
    return crud.create_image(db=db, image=image)


@app.get("/v1/images/", response_model=list[schemas.Image])
def get_images(skip: int = 0, limit: int = 100,
               gender: models.Gender = None,
               race: models.Race = None,
               db: Session = Depends(get_db)):
    users = crud.get_images(db, skip=skip, limit=limit, race=race, gender=gender)
    return users


@app.get("/v1/images/{image_id}", response_model=schemas.Image)
def get_image_by_id(image_id: str, db: Session = Depends(get_db)):
    db_image = crud.get_image_by_id(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image


@app.get("/v1/images/{file_name}", response_model=schemas.Image)
def get_image_by_file_name(file_name: str, db: Session = Depends(get_db)):
    db_image = crud.get_image_by_file_name(db, file_name=file_name)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image
