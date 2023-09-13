import ast
import os

import pandas as pd
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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


@app.get("/v1/images/sample/")
def get_sample_batch(limit: int = 25):
    df = pd.read_csv("merged.csv")

    # df = df[df["accepted"].isna()]
    # print(len(df))
    df = df.sample(n=limit)

    if limit is None:
        df = df.iloc[:]
    else:
        df = df.iloc[:limit]

    filtered_df = df.dropna(axis=1, how='all')

    df_without_accepted = filtered_df.drop(columns=['accepted'])

    return df_without_accepted.to_dict(orient='records')


@app.get("/v1/images/{image_name}/")
async def get_image(image_name: str):
    image_path = os.path.join("./images", image_name)
    if not os.path.exists(image_path):
        print(image_path)
        raise Exception()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return Response(content=image_bytes, media_type="image/png")


@app.post("/v1/images/sample/")
async def submit_sample_batch_result(request: Request):
    data = await request.json()
    df = pd.read_csv("merged.csv")
    for filename, accepted in data.items():
        row = df[df['filename'] == filename]

        if row.empty:
            df = df.append({'filename': filename, 'accepted': [accepted]}, ignore_index=True)
        else:
            current_accepted = row['accepted'].iloc[0]
            if pd.isna(current_accepted):
                current_accepted = []
            else:
                current_accepted = ast.literal_eval(current_accepted)
            current_accepted.append(accepted)
            df.loc[df['filename'] == filename, 'accepted'] = pd.Series([current_accepted] * len(df))

    df.to_csv("merged.csv", index=False)
