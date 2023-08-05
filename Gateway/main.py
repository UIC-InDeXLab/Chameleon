import datetime
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile

import services
from models import MaximalUncoveredPattern
from utils import store_png_files, store_mup

load_dotenv()

app = FastAPI()

logger = logging.getLogger(__name__)


@app.post("/v1/mup/images")
async def generate_images(mup_list: UploadFile, threshold: int):
    def store_outputs(mup, base, mask, final):
        current_time = datetime.datetime.now()
        dir_name = f"./results/{current_time}"
        file_name = f"{'_'.join(list(mup.pattern))}_{current_time.strftime('%Y%m%d%H%M%S%f')}.png"
        store_png_files(["base.png", "mask.png", file_name], [base, mask, final], dir_name)
        store_mup(mup, "mup.json", dir_name)
        mup.add_image(f"{dir_name}/{file_name}")
        logger.debug(
            f"new {mup.pattern}/{mup.prompt} generated: {dir_name}, # remaining: {mup.get_count_needed(threshold)}")
        return dir_name

    mup_strings = mup_list.file.read().decode(encoding='utf-8')
    mups = await create_mups(mup_strings)
    while len(mups) != 0:
        mup = mups.pop(0)
        while not mup.is_satisfied(threshold):
            base_image = services.get_mup_random_image(mup)
            mask = services.get_mask(base_image)
            generated_image_json = services.generate_image_by_prompt(base_image, mask, mup.prompt)
            new_image_url = json.loads(generated_image_json.decode("utf-8"))["data"][0]["url"]
            final_image = services.get_image_from_url(new_image_url)
            store_outputs(mup, base_image, mask, final_image)


async def create_mups(mup_strings) -> list[MaximalUncoveredPattern]:
    mups: list[MaximalUncoveredPattern] = []
    for pattern in mup_strings.splitlines():
        count, prompt = services.get_pattern_details(pattern)
        mups.append(MaximalUncoveredPattern(pattern=pattern, frequency=count, prompt=prompt))
    return mups
