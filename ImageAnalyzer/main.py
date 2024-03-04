import datetime
import json
import random
import uuid
from typing import List

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query

import csv_crud
from greedy_mup_selector import MUPTree
from models import DatasetManager, Dataset
from utils import assert_env_var_not_none, convert_list_to_dict

load_dotenv()


def load_datasets():
    with open(assert_env_var_not_none("CONFIG_FILE_PATH"), 'r+') as f:
        config = json.load(f)
    datasets = config["datasets"]
    manager: DatasetManager = DatasetManager.instance()
    for d in datasets:
        manager.add_dataset(Dataset(**d))


app = FastAPI(on_startup=[load_datasets])


@app.get("/v1/datasets/")
def get_available_datasets():
    manager: DatasetManager = DatasetManager.instance()
    return manager.get_datasets()


@app.get("/v1/datasets/{dataset_id}/")
def get_dataset_details(dataset_id: str):
    manager: DatasetManager = DatasetManager.instance()
    parent = manager.get_parent_dataset(dataset_id)
    count = csv_crud.get_images_count(ds_id=dataset_id)
    result = {"attributes": parent.attributes, "id": dataset_id, "parent": parent.name, "count": count}
    return result


@app.post("/v1/datasets/")
def create_sample_dataset(parent: str, name: str, num_rows: int):
    manager: DatasetManager = DatasetManager.instance()
    df = csv_crud.get_partial_table_df(ds_id=parent, limit=num_rows)
    id = str(uuid.uuid4())[:6]
    filename = f"{parent}_{name}_{id}"
    df.to_csv(f"./datasets/{filename}.csv", index=False)

    return {"id": filename}


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


@app.post("/v1/images/datasets/{dataset_id}/random/")
def add_random_images_to_dataset(dataset_id: str, gender: str, race: str, age_group: str, count: int = 1):
    with open(f"datasets/{dataset_id}.csv", 'a') as f:
        for i in range(count):
            current_time = datetime.datetime.now()
            filename = f"{age_group}_{gender}_{race}_{current_time.strftime('%Y%m%d%H%M%S%f')}_fake.png"
            f.write(f"{filename},{age_group},{gender},{race},True\n")

    return {"success": True}


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
    prompt = manager.get_parent_dataset(dataset_id).get_prompt(convert_list_to_dict(filters))
    count = csv_crud.get_images_count(ds_id=dataset_id, filters=convert_list_to_dict(filters),
                                      is_generated=None if include_generated_images else False)

    return {"count": count, "prompt": prompt}


@app.get("/v1/combinations/datasets/{dataset_id}/status/")
def get_all_combinations_status(dataset_id: str):
    manager: DatasetManager = DatasetManager.instance()
    dataset = manager.get_first_dataset()
    res = {}
    for age_group in range(0, 8):
        for gender in range(0, 2):
            for race in range(0, 4):
                res[f"{age_group}{gender}{race}"] = csv_crud.get_images_count(dataset_id,
                                                                              {"age_group": age_group, "gender": gender,
                                                                               "race": race})
    return res


@app.get("/v1/datasets/{dataset_id}/mups/")
def get_best_mup(dataset_id: str, threshold: int):
    def does_hit(pat: str, comb: str) -> bool:
        for i, c in enumerate(list(pat)):
            if c == "x":
                continue
            if comb[i] != c:
                return False
        return True

    manager: DatasetManager = DatasetManager.instance()
    parent_ds = manager.get_parent_dataset(dataset_id)
    mups_patterns: list[str] = csv_crud.get_mups(dataset_id, threshold, parent_ds.num_attributes,
                                                 parent_ds.cardinality_of_attributes, parent_ds.attributes_ids)
    mups_level_dict = {}
    for pattern in mups_patterns:
        v = mups_level_dict.setdefault(pattern.count("x"), [])
        v.append(pattern)

    patterns_to_fix = mups_level_dict.get(max(mups_level_dict.keys()))
    tree = MUPTree(parent_ds.num_attributes, parent_ds.cardinality_of_attributes, patterns_to_fix)

    best_combination = random.choice(tree.get_best_combinations()).pattern
    mups_candidates = {}
    for p in patterns_to_fix:
        c_filters = [f"{parent_ds.get_attribute_by_column_number(parent_ds.attributes_ids[i]).name}={c}" for i, c in
                     enumerate(list(best_combination)) if c != 'x']
        if does_hit(p, best_combination):
            filters = [f"{parent_ds.get_attribute_by_column_number(parent_ds.attributes_ids[i]).name}={c}" for i, c in
                       enumerate(list(p)) if c != 'x']
            mups_candidates[p] = {"count": csv_crud.get_images_count(dataset_id, filters=convert_list_to_dict(filters)),
                                  "prompt": parent_ds.get_prompt(filters=convert_list_to_dict(c_filters)),
                                  "pmup": p,
                                  "pattern": best_combination
                                  }

    mups_result_dict = {}

    for pattern in mups_patterns:
        filters = [f"{parent_ds.get_attribute_by_column_number(parent_ds.attributes_ids[i]).name}={c}" for i, c in
                   enumerate(list(pattern)) if c != "x"]
        mups_result_dict[pattern] = {
            "count": csv_crud.get_images_count(dataset_id, filters=convert_list_to_dict(filters)),
            "prompt": parent_ds.get_prompt(filters=convert_list_to_dict(filters)),
            "level": len(list(pattern)) - pattern.count("x")
        }

    res = {k: v for k, v in sorted(mups_candidates.items(), key=lambda item: item[1]["count"], reverse=True)}
    for k, v in res.items():
        print(k, v["count"])
    k = list(res.keys())[0]
    return {"best_mups": {best_combination: res[k]}, "mups": mups_result_dict, "attributes": parent_ds.attributes}


@app.post("/v1/images/export/partial/")
async def export_partial_dataset(request: Request):
    data = await request.json()
    df_to_merge = []
    for i, ag in enumerate(data["age_groups"]):
        filters = {}
        age_group_str, age_group_dict = ag.popitem()
        filters['age_group'] = int(age_group_str)
        for g, races_dict in age_group_dict.items():
            filters['gender'] = int(g)
            for r, count in races_dict.items():
                filters['race'] = int(r)
                df_to_merge.append(
                    csv_crud.get_partial_table_df(ds_id="main", filters=filters, limit=int(count)))

    merged_df = pd.concat(df_to_merge, axis=0, ignore_index=True)

    id = str(uuid.uuid4())
    merged_df.to_csv(f"./datasets/{id}.csv", index=False)

    return {"id": id}
