import json
import uuid
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query

import csv_crud
from greedy_mup_selector import MUPTree
from models import DatasetManager, Dataset
from utils import assert_env_var_not_none, timeit, convert_list_to_dict

load_dotenv()


def load_datasets():
    with open(assert_env_var_not_none("CONFIG_FILE_PATH"), 'r+') as f:
        config = json.load(f)
    datasets = config["datasets"]
    manager: DatasetManager = DatasetManager.instance()
    for d in datasets:
        manager.add_dataset(Dataset(**d))


@timeit
def load_images():
    pass


app = FastAPI(on_startup=[load_datasets, load_images])


@app.get("/v1/datasets/details/")
def get_current_main_dataset_details():
    pass


@app.get("/v1/datasets/{dataset_id}/images/")
def get_images(dataset_id: str, skip: int = 0, limit: int = None, is_generated: bool = None,
               filters: List[str] = Query(None)):
    images = csv_crud.get_images(ds_id=dataset_id, skip=skip, limit=limit, filters=convert_list_to_dict(filters),
                                 is_generated=is_generated)
    return images.to_dict(orient="records")


@app.post("/v1/datasets/{dataset_id}/{file_name}/")
def add_image_to_dataset(dataset_id: str, file_name: str, attributes: List[str] = Query(None)):
    csv_crud.add_image(dataset_id, file_name, convert_list_to_dict(attributes), is_generated=True)
    return {"file_name": file_name}


@app.get("/v1/datasets/{dataset_id}/images/{file_name}/details/")
def get_image_details(dataset_id: str, file_name: str):
    db_image = csv_crud.get_image(ds_id=dataset_id, filename=file_name)
    return db_image.to_dict()


@app.get("/v1/datasets/{dataset_id}/images/count/")
def get_images_count(dataset_id: str, filters: List[str] = Query(None), is_generated: bool = None):
    count = csv_crud.get_images_count(ds_id=dataset_id, filters=convert_list_to_dict(filters),
                                      is_generated=is_generated)
    return {"count": count}


@app.get("/v1/datasets/{dataset_id}/images/random/")
async def get_random_image_from_dataset(dataset_id: str, filters: List[str] = Query(None),
                                        include_generated_images: bool = False):
    db_image = csv_crud.get_random_image(ds_id=dataset_id, filters=convert_list_to_dict(filters),
                                         is_generated=None if include_generated_images else False)

    return db_image.to_dict()


@app.get("/v1/datasets/{dataset_id}/images/prompt/")
def generate_prompt(dataset_id: str, filters: List[str] = Query(None), include_generated_images: bool = True):
    manager: DatasetManager = DatasetManager.instance()
    prompt = manager.get_dataset().get_prompt(convert_list_to_dict(filters))
    count = csv_crud.get_images_count(ds_id=dataset_id, filters=convert_list_to_dict(filters),
                                      is_generated=None if include_generated_images else False)

    return {"count": count, "prompt": prompt}


@app.get("/v1/datasets/{dataset_id}/mups/")
def get_best_mup(dataset_id: str, threshold: int):
    manager: DatasetManager = DatasetManager.instance()
    dataset = manager.get_dataset()
    mups: list[str] = csv_crud.get_mups(dataset_id, threshold, dataset.num_attributes,
                                        dataset.cardinality_of_attributes, dataset.attributes_ids)
    mups_dict = {}
    for m in mups:
        v = mups_dict.setdefault(m.count("x"), [])
        v.append(m)

    tree = MUPTree(dataset.num_attributes, dataset.cardinality_of_attributes, mups_dict.get(max(mups_dict.keys())))
    results = tree.get_best_combinations()
    results_dict = {}
    for node in results:
        filters = [f"{dataset.get_attribute_by_column_number(dataset.attributes_ids[i]).name}={c}" for i, c in
                   enumerate(list(node.pattern))]
        results_dict[node.pattern] = csv_crud.get_images_count(dataset_id, filters=convert_list_to_dict(filters))

    res = {k: v for k, v in sorted(results_dict.items(), key=lambda item: item[1])}
    return {"best_mups": res, "mups": mups}


@app.post("/v1/images/export/partial/")
async def export_partial_dataset(request: Request):
    data = await request.json()
    df = None
    # TODO: need to be done asap
    id = str(uuid.uuid4())
    df.to_csv(f"./datasets/{id}.csv", index=False)

    return {"id": id}
