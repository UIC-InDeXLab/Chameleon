import datetime
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import services
from models import MaximalUncoveredPattern
from utils import store_png_files, store_mup, load_image

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
        mask_dir, base_dir, mup_dir = os.path.join(dir_name, "masks"), os.path.join(dir_name, "base_images"),  os.path.join(dir_name, "mups")
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

    frequency, prompt = services.get_pattern_details(dataset_id, pattern)
    mup = MaximalUncoveredPattern(pattern=pattern, frequency=frequency, prompt=prompt)
    num_generated = 0
    while not mup.is_satisfied(threshold) and num_generated < limit:
        try:
            if strategy == "none":
                generated_image_json = services.generate_image(mup.prompt)
                new_image_url = generated_image_json["data"][0]["url"]
                final_image = services.get_image_from_url(new_image_url)
                store_outputs(mup, final_image)
            else:
                base_image_details = services.get_mup_similar_image(dataset_id, mup) if strategy == "similar" \
                    else services.get_random_image(dataset_id)
                base_image = load_image(base_image_details["filename"], base_image_details["is_generated"])
                mask = services.get_mask(base_image, accuracy)
                generated_image_json = services.edit_image(base_image, mask, mup.prompt)
                new_image_url = json.loads(generated_image_json.decode("utf-8"))["data"][0]["url"]
                final_image = services.get_image_from_url(new_image_url)
                file_name = store_outputs(mup, final_image)
                store_metadata(file_name, mup, base_image, mask)

            num_generated += 1
        except Exception:
            continue

    return {"generated_images": mup.generated_images}


@app.get("/v1/datasets/{dataset_id}/mups/")
async def get_mups(dataset_id: str, threshold: int):
    best_mups_patterns, mups_patterns = services.get_mups_details(dataset_id, threshold)
    mups_details, best_mups_details = [], []

    for p in mups_patterns:
        count, prompt = services.get_pattern_details(dataset_id, p)
        mups_details.append(MaximalUncoveredPattern(p, count, prompt))
    for p in best_mups_patterns:
        count, prompt = services.get_pattern_details(dataset_id, p)
        best_mups_details.append(MaximalUncoveredPattern(p, count, prompt))

    return {"mups": mups_details, "best_mups": best_mups_details}


@app.post("/v1/datasets/{dataset_id}/images/")
async def submit_acceptable_images(dataset_id: str, request: Request):
    data = await request.json()
    acceptable_images = data["acceptable_images"]
    for image in acceptable_images:
        services.add_image_to_dataset(dataset_id, image)
    return {"success": True}


@app.get("/v1/datasets/{dataset_id}/")
def get_dataset_details(dataset_id: str):
    result = services.get_dataset_details(dataset_id)
    return result


@app.post("/v1/datasets/")
async def export_partial_dataset(request: Request):
    data = await request.json()
    return services.create_partial_ds(data)


@app.get("/v1/image/{dataset_id}/{image_name}/")
async def get_image(dataset_id: str, image_name: str, is_generated: bool = None):
    if is_generated is None:
        is_generated = services.get_image_details(dataset_id, image_name)["is_generated"]

    if is_generated:
        image_path = os.path.join(os.getenv("GENERATION_PATH"), dataset_id, image_name)
    else:
        image_path = os.path.join(os.getenv("RESOURCES_PATH"), image_name)
    if not os.path.exists(image_path):
        raise Exception()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return Response(content=image_bytes, media_type="image/png")
