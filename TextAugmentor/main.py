import os

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI, AsyncOpenAI

from enums import Emotion

load_dotenv()
app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-pro')


@app.post("/v1/api/sentiment/")
async def edit_sentiment(text: str, source_emotion: Emotion, des_emotion: Emotion):
    # prompt = f"rewrite and change the sentiment of this text from {source_emotion.name} to {des_emotion.name}:\n\n{text}"
    # prompt = f"rewrite and change this sentence with sentiment {des_emotion}:\n\n{text}"
    prompt = f"imagine you have {des_emotion.name} emotion right now and write a tweet about it, include just text, no hashtags, no emojis"
    print(prompt)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=400,
            n=1,
            temperature=1.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # response = model.generate_content(prompt)
        return {"result": response.choices[0].message.content}
        # return {"result": response.text.lower()}
    except Exception as e:
        # print(response.prompt_feedback)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/api/augment/")
async def augment_dataset(dataset_id: str, emotion_to_augment: Emotion, count: int):
    df = pd.read_csv(f"datasets/{dataset_id}")
    augmented_data = []
    i = 0
    while i < count:
        # Select a random row where the label is not the emotion_to_augment
        suitable_rows = df[df['label'] == emotion_to_augment]
        if suitable_rows.empty:
            raise HTTPException(status_code=404, detail="Not enough data to augment")

        row = suitable_rows.sample(n=1).iloc[0]
        try:
            new_text_result = await edit_sentiment(row['text'], Emotion(row['label']), emotion_to_augment)
            augmented_data.append({'text': new_text_result['result'], 'label': emotion_to_augment})
            i = i + 1
            print(i)
        except Exception as e:
            print(e)
            continue

    # Create DataFrame from the augmented data
    augmented_df = pd.DataFrame(augmented_data)
    augmented_df.to_csv(f"datasets/augmented_{dataset_id.replace('.csv', '')}_{emotion_to_augment.name.lower()}.csv",
                        index=False)
    return {"message": "Dataset augmented successfully", "augmented_file": f"augmented_{dataset_id}"}
