import json

from fastapi import FastAPI, UploadFile
from models import MUP


def load_config():
    with open('config.json') as f:
        data = json.load(f)
        m = MUP("101", None)
        m.weights = data["pattern_weights"]


app = FastAPI(on_startup=[load_config])


@app.post("/v1/mup/images")
async def generate_images(mup_list: UploadFile, threshold: int):
    mups = mup_list.read()
