import io
import crud
import models
import schemas
import os
import json
import pandas as pd

from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from utils import assert_env_var_not_none, timeit
from models import AgeGroup, AgeGroupManager

load_dotenv()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_age_groups_manager():
    with open('config.json', 'r') as f:
        data = json.load(f)
    age_groups = [AgeGroup(id=i, **age_group) for i, age_group in enumerate(data['age_groups'])]
    manager = AgeGroupManager(age_groups)
    return manager


@timeit
def load_images():
    db = next(get_db())
    path = assert_env_var_not_none("RESOURCES_PATH")
    for image_file in os.listdir(path):
        try:
            crud.create_image_by_filename(db=db, filename=os.path.basename(image_file))
        except Exception as e:
            print(f"Error in filename: {image_file}, {e}")
            continue
    print("Images loaded successfully.")


# app = FastAPI(on_startup=[get_db, load_images])
app = FastAPI(on_startup=[get_db, init_age_groups_manager])


@app.post("/v1/images/", response_model=schemas.Image)
def create_user(image: schemas.ImageCreate, db: Session = Depends(get_db)):
    return crud.create_image(db=db, image=image)


@app.get("/v1/images/", response_model=list[schemas.Image])
def get_images(skip: int = 0, limit: int = 100,
               gender: models.Gender = None,
               race: models.Race = None,
               min_age: int = 0,
               max_age: int = 200,
               db: Session = Depends(get_db)):
    users = crud.get_images(db, skip=skip, limit=limit, race=race, gender=gender, min_age=min_age, max_age=max_age)
    print(len(users))
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


@app.get("/v1/images/export/")
async def export_csv(db: Session = Depends(get_db), manager: AgeGroupManager = Depends(init_age_groups_manager)):
    results = crud.get_table_df(db, manager)
    df = pd.DataFrame(columns=['filename', 'age', 'gender', 'race'],
                      data=[[r.filename, r.age, r.gender, r.race] for r
                            in results])

    return StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data.csv"})
