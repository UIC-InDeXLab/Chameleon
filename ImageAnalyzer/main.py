import json
import os

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from tqdm import tqdm

import crud
import models
import schemas
from database import SessionLocal, engine
from models import AgeGroup, AgeGroupGenderRacePattern
from utils import assert_env_var_not_none, timeit, get_image_full_path

load_dotenv()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@timeit
def load_images():
    if os.getenv("RELOAD_IMAGES", "False").lower() not in ['true', '1']:
        return
    db = next(get_db())
    path = assert_env_var_not_none("RESOURCES_PATH")
    try:
        db.query(models.Image).delete()
        db.commit()
        print("DB cleared.")
    except Exception:
        db.rollback()

    for image_file in tqdm(os.listdir(path)):
        try:
            crud.create_image_by_filename(db=db, filename=os.path.basename(image_file))
        except Exception as e:
            print(f"Error in filename: {image_file}, {e}")
            continue
    print("Images loaded successfully.")


app = FastAPI(on_startup=[get_db, load_images])


@app.get("/v1/images/", response_model=list[schemas.Image])
def get_images(skip: int = 0, limit: int = None,
               gender: models.Gender = None,
               race: models.Race = None,
               age_group: models.AgeGroup = None,
               db: Session = Depends(get_db)):
    users = crud.get_images(db, skip=skip, limit=limit, race=race, gender=gender, age_group=age_group)
    return users


@app.get("/v1/images/pattern/{pattern}/", response_class=FileResponse)
async def get_random_image_by_pattern(pattern: str, db: Session = Depends(get_db)):
    p = AgeGroupGenderRacePattern(pattern)
    db_image = crud.get_random_image(db=db, gender=p.gender, race=p.race, age_group=p.age_group)
    return FileResponse(get_image_full_path(db_image.filename))


@app.get("/v1/images/export/")
async def export_csv(db: Session = Depends(get_db)):
    results = crud.get_table_df(db)
    df = pd.DataFrame(columns=['filename', 'age_group', 'gender', 'race'],
                      data=[[r.filename, r.age_group, r.gender, r.race] for r in results])

    return StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data.csv"})


@app.get("/v1/prompt/{pattern}/")
def generate_prompt(pattern: str, db: Session = Depends(get_db)):
    p = AgeGroupGenderRacePattern(pattern)
    count = crud.get_images_count(db=db, race=p.race, gender=p.gender, age_group=p.age_group)
    return {"count": count, "prompt": p.prompt}


@app.get("/v1/images/count/")
def def_images_count(gender: models.Gender = None,
                     race: models.Race = None,
                     age_group: models.AgeGroup = None,
                     db: Session = Depends(get_db)):
    count = crud.get_images_count(db=db, race=race, gender=gender, age_group=age_group)
    return {"count": count}
