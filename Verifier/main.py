import ast
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

load_dotenv()

origins = ["http://localhost:3000", "http://127.0.0.1:3000", os.getenv("PUBLIC_IP", "http://127.0.0.1:3000")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

original_images_df = pd.read_csv("datasets/original_images.csv")
generated_images_df = pd.read_csv("datasets/all_generated_accepted.csv")
results_df = pd.read_csv("datasets/results.csv")


@app.get("/v1/images/sample/")
async def get_images():
    original_filtered = original_images_df.sample(n=6)
    generated_filtered = generated_images_df.sample(n=3)

    selected_images = pd.concat([original_filtered, generated_filtered])

    res_df = selected_images.drop(columns=['strategy', 'mask_level'])
    res_df = res_df.iloc[np.random.permutation(len(res_df))]
    return res_df.to_dict(orient="records")


@app.get("/v1/images/{image_name}/")
async def get_image(image_name: str):
    df = pd.read_csv("datasets/all_generated_accepted.csv")
    row = df[df['filename'] == image_name]

    if row.empty:
        image_path = os.path.join(os.environ["ORIGINAL_RESOURCES_PATH"], image_name)
    else:
        image_path = os.path.join(os.environ["GENERATED_RESOURCES_PATH"], image_name)

    if not os.path.exists(image_path):
        print(image_path)
        raise Exception()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return Response(content=image_bytes, media_type="image/png")


@app.post("/v1/images/sample/")
async def mark_images(request: Request):
    data = await request.json()
    df = pd.read_csv("datasets/results.csv")
    acceptable_results = ["1", "true", "t"]

    for filename, marked_str in data.items():
        marked = True if str(marked_str).lower() in acceptable_results else False
        marked = not marked
        row = df[df['filename'] == filename]

        if row.empty:
            new_row_df = pd.DataFrame([{'filename': filename, 'marked': str([marked])}])
            df = pd.concat([df, new_row_df], ignore_index=True)
        else:
            current_accepted = row['marked'].iloc[0]
            if pd.isna(current_accepted):
                current_accepted = []
            else:
                current_accepted = ast.literal_eval(current_accepted)
            current_accepted.append(marked)
            df.loc[df['filename'] == filename, 'marked'] = pd.Series([current_accepted] * len(df))

    df.to_csv("datasets/results.csv", index=False)
