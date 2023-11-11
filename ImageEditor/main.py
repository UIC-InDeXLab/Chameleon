import os

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from openai import OpenAI, AsyncOpenAI

load_dotenv()
app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.post("/v1/images/edits")
async def edit_image(image: UploadFile, prompt: str, mask: UploadFile = None, n: int = 4, size: str = "512x512"):
    return await aclient.images.edit(image=image.file.read(), mask=mask.file.read() if mask else None,
                                     prompt=prompt, n=n, size=size)


@app.post("/v1/images/generations")
async def generate_image(prompt: str, n: int = 4, size: str = "512x512"):
    return await aclient.images.generate(prompt=prompt, n=n, size=size)
