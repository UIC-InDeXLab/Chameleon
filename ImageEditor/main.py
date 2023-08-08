import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile

load_dotenv()
app = FastAPI()

openai.organization = os.getenv("OPENAI_ORGANIZATION_NAME")
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.post("/v1/images/edits")
async def edit_image(image: UploadFile, prompt: str, mask: UploadFile = None, n: int = 4, size: str = "512x512"):
    return await openai.Image.acreate_edit(image=image.file.read(), mask=mask.file.read() if mask else None,
                                           prompt=prompt, n=n, size=size)
