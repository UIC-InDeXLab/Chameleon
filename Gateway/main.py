import datetime
import json
import logging
import os
from time import sleep

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import services
from models import MaximalUncoveredPattern, Attribute
from utils import store_png_files, store_mup, load_image, convert_list_to_dict

load_dotenv()

app = FastAPI()

origins = ["http://localhost:3000", "http://127.0.0.1:3000", os.getenv("PUBLIC_IP", "http://127.0.0.1:3000")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/v1/datasets/{dataset_id}/mups/generate/")
async def generate_images(dataset_id: str, request: Request):
    def store_outputs(mup, final):
        current_time = datetime.datetime.now()
        dir_name = os.path.join(os.getenv("GENERATION_PATH"), dataset_id)
        file_name = f"{'_'.join(list(mup.pattern))}_{current_time.strftime('%Y%m%d%H%M%S%f')}"
        store_png_files(dir_name, [f"{file_name}.png"], [final])
        mup.add_image(f"{dataset_id}/{file_name}.png")
        logger.info(
            f"new {mup.pattern}/{mup.prompt} generated: {dir_name}, # remaining: {mup.get_count_needed(threshold)}")
        return file_name

    def store_metadata(file_name, mup, base, mask):
        dir_name = os.path.join(os.getenv("GENERATION_PATH"), dataset_id)
        mask_dir, base_dir, mup_dir = os.path.join(dir_name, "masks"), os.path.join(dir_name,
                                                                                    "base_images"), os.path.join(
            dir_name, "mups")
        store_png_files(mask_dir, [f"{file_name}.png"], [mask])
        store_png_files(base_dir, [f"{file_name}.png"], [base])
        store_mup(mup, f"{file_name}.json", mup_dir)
        return file_name

    data = await request.json()
    pattern = data["pattern"]
    threshold = int(data["threshold"])
    limit = int(data["limit"])
    strategy = data["strategy"]
    accuracy = data["accuracy"]
    frequency = data["frequency"]
    prompt = data["prompt"]
    attributes = data["attributes"]
    use_parent_for_embeddings = data.get("use_parent_for_embeddings", False)

    parent = dataset_id.strip().split("_").pop(0)
    need_to_be_generated = threshold - frequency

    mup = MaximalUncoveredPattern(pattern=pattern, frequency=frequency, prompt=prompt,
                                  attributes=[Attribute(**a) for a in attributes])
    num_generated = 0
    while num_generated < need_to_be_generated and num_generated < limit:
        try:
            if strategy == "none":
                generated_image_json = services.generate_image(mup.prompt)
                new_image_url = generated_image_json["data"][0]["url"]
                final_image = services.get_image_from_url(new_image_url)
                store_outputs(mup, final_image)
                ddt_result = True
                mup.ddt_results.append(ddt_result)
            else:
                if strategy == "similar":
                    base_image_details = services.get_mup_similar_image(dataset_id, mup)
                elif strategy == "ucb":
                    base_image_details = services.get_mup_ucb(dataset_id, mup)
                else:
                    base_image_details = services.get_random_image(dataset_id)

                base_image = load_image(base_image_details["filename"], parent, base_image_details["is_generated"])
                mask = services.get_mask(base_image, accuracy)
                generated_image_json = services.edit_image(base_image, mask, mup.prompt)
                new_image_url = json.loads(generated_image_json.decode("utf-8"))["data"][0]["url"]
                final_image = services.get_image_from_url(new_image_url)
                train_image_paths = set(
                    [os.path.join(os.getenv("RESOURCES_PATH"), parent, image["filename"]) for image in
                     services.get_dataset_images(
                         dataset_id=parent if use_parent_for_embeddings else dataset_id, is_generated=False)])
                # ddt_result = services.get_data_distribution_test_result(final_image, train_paths=train_image_paths)[
                #     "prediction"]
                ddt_result = True
                mup.ddt_results.append(ddt_result)
                file_name = store_outputs(mup, final_image)
                store_metadata(file_name, mup, base_image, mask)

            num_generated += 1
        except Exception as e:
            print(e)
            sleep(1)
            continue

    return {"generated_images": mup.generated_images, "pulled_arms": mup.pulled_arms, "ddt_results": mup.ddt_results}


@app.get("/v1/datasets/{dataset_id}/mups/")
async def get_mups(dataset_id: str, threshold: int):
    mup_details = services.get_mups_details(dataset_id, threshold)
    return mup_details


@app.post("/v1/datasets/{dataset_id}/mups/{pattern}/status/")
async def get_pattern_details(dataset_id: str, pattern: str, threshold: int, request: Request):
    data = await request.json()
    attributes = data["attributes"]
    mup_status = services.get_pattern_details(dataset_id, pattern, attributes=[Attribute(**a) for a in attributes])
    mup_status["is_satisfied"] = True if threshold <= mup_status["count"] else False
    return mup_status


@app.post("/v1/datasets/{dataset_id}/images/")
async def submit_acceptable_images(dataset_id: str, request: Request):
    data = await request.json()
    images: dict = data["images"]
    attributes = data["attributes"]
    pattern = data["pattern"]
    for image in images:
        if image["accepted"]:
            services.add_image_to_dataset(dataset_id, image["name"], pattern,
                                          attributes=[Attribute(**a) for a in attributes])
        if image.get("arm", None) is not None:
            services.update_ucb(image["arm"], pattern, 1 if image["accepted"] else 0)
    return {"success": True}


@app.get("/v1/datasets/{dataset_id}/images/")
async def get_dataset_images(dataset_id: str, skip: int = 0, limit: int | None = None,
                             filters: str = None, is_generated: bool | None = None):
    filters_list = [f for f in filters.split("&") if not f.lower().endswith("=all")] if filters is not None else None
    images = services.get_dataset_images(dataset_id, skip, limit,
                                         filters=convert_list_to_dict(filters_list),
                                         is_generated=is_generated)

    return {"images": [img["filename"] for img in images]}


@app.get("/v1/datasets/")
def get_available_datasets():
    result = services.get_available_datasets()
    return result


@app.post("/v1/datasets/")
async def create_dataset(request: Request):
    data = await request.json()
    parent = data["parent"]
    name = data["name"]
    number = data["number"]
    return services.create_sample_ds(parent, name, number)


@app.get("/v1/datasets/{dataset_id}/")
def get_dataset_details(dataset_id: str):
    result = services.get_dataset_details(dataset_id)
    return result


@app.get("/v1/image/{dataset_id}/{image_name}/")
async def get_image(dataset_id: str, image_name: str, is_generated: bool = None):
    if is_generated is None:
        is_generated = services.get_image_details(dataset_id, image_name)["is_generated"]

    if is_generated:
        image_path = os.path.join(os.getenv("GENERATION_PATH"), dataset_id, image_name)
    else:
        parent = dataset_id.strip().split("_").pop(0)
        image_path = os.path.join(os.getenv("RESOURCES_PATH"), parent, image_name)
    if not os.path.exists(image_path):
        print(image_path)
        raise Exception()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return Response(content=image_bytes, media_type="image/png")
