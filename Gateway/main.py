import datetime
import json
import random

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile

import services
from models import MUP
from utils import store_png_files, store_mup

load_dotenv()


def load_config():
    with open('config.json') as f:
        data = json.load(f)
        m = MUP(None, None, None)
        m.weights = data["pattern_weights"]


app = FastAPI(on_startup=[load_config])


@app.post("/v1/mup/images")
async def generate_images(mup_list: UploadFile, threshold: int):
    mup_strings = mup_list.file.read().decode(encoding='utf-8')
    mups = await create_mups(mup_strings)
    while len(mups) != 0:
        idx = mups.index(random.choice(mups))
        mup = mups[idx]
        base_image = services.get_mup_random_image(mup)
        mask = services.get_mask(base_image)
        generated_image = services.generate_image_by_prompt(base_image, mask, mup.prompt)
        new_image_url = json.loads(generated_image.decode("utf-8"))["data"][0]["url"]
        final_image = services.get_image_from_url(new_image_url)
        dir_name = f"./results/{'_'.join(list(mup.pattern))}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        store_png_files(["base.png", "mask.png", "final.png"], [base_image, mask, final_image], dir_name)
        store_mup(mup, "mup.json", dir_name)
        mup.add_image(dir_name + "/final.png")
        print(
            f"new {mup.pattern}/{mup.prompt} image generated, dir: {dir_name}, count needed {mup.get_count_needed(threshold)}")
        if mup.is_satisfied(threshold):
            mups.pop(idx)


async def create_mups(mup_strings) -> list[MUP]:
    mups: list[MUP] = []
    for pattern in mup_strings.splitlines():
        count, prompt = services.get_pattern_details(pattern)
        mups.append(MUP(pattern=pattern, count=count, prompt=prompt))
    return mups
