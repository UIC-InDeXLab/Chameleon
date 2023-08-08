import os
import uuid

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from tqdm import tqdm

import crud
import csv_crud
import models
import schemas
from database import SessionLocal, engine
from models import AgeGroupGenderRacePattern, AgeGroup, Race, Gender
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

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/{dataset_id}/images/", response_model=list[schemas.ExportImageBase])
def get_images(dataset_id: str, skip: int = 0, limit: int = None,
               gender: models.Gender = None,
               race: models.Race = None,
               age_group: models.AgeGroup = None):
    users = csv_crud.get_images(ds_id=dataset_id, skip=skip, limit=limit, race=race, gender=gender, age_group=age_group)
    return [
        schemas.ExportImageBase.model_construct(
            filename=r["filename"], age_group=r["age_group"], gender=r["gender"],
            race=r["race"]) for r in users.to_dict(orient="records")]


@app.get("/v1/{dataset_id}/images/pattern/{pattern}/", response_class=FileResponse)
async def get_random_image_by_pattern(dataset_id: str, pattern: str):
    p = AgeGroupGenderRacePattern(pattern)
    db_image = csv_crud.get_random_image(ds_id=dataset_id, gender=p.gender, race=p.race, age_group=p.age_group)
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


@app.get("/v1/{dataset_id}/prompt/{pattern}/")
def generate_prompt(dataset_id: str, pattern: str):
    p = AgeGroupGenderRacePattern(pattern)
    count = csv_crud.get_images_count(ds_id=dataset_id, race=p.race, gender=p.gender, age_group=p.age_group)
    return {"count": count, "prompt": p.prompt}


@app.get("/v1/{dataset_id}/images/count/")
def get_images_count(dataset_id: str,
                     gender: models.Gender = None,
                     race: models.Race = None,
                     age_group: models.AgeGroup = None):
    count = csv_crud.get_images_count(ds_id=dataset_id, race=race, gender=gender, age_group=age_group)
    return {"count": count}


@app.post("/v1/images/export/partial/")
async def export_partial_dataset(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    dataset = []
    for i, ag in enumerate(data["age_groups"]):
        age_group_str, age_group_dict = ag.popitem()
        age_group = getattr(AgeGroup, str(age_group_str).lower().replace(" ", "_"))
        for g, races_dict in age_group_dict.items():
            gender = getattr(Gender, str(g).lower())
            for r, count in races_dict.items():
                race = getattr(Race, str(r).lower())
                dataset.extend(
                    crud.get_partial_table_df(db=db, gender=gender, race=race, age_group=age_group, limit=int(count)))

    df = pd.DataFrame(columns=['filename', 'age_group', 'gender', 'race'],
                      data=[[r.filename, r.age_group, r.gender, r.race] for r in dataset])

    id = str(uuid.uuid4())
    df.to_csv(f"./datasets/{id}.csv", index=False)

    return {"id": id}
