from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile

from models import OCSVMModel, ImageEmbedder
from utils import download_embedder, create_set_hash

load_dotenv()


def init_embedder():
    download_embedder()


app = FastAPI(on_startup=[init_embedder])

active_embeddings = {}


@app.post("/v1/predict/")
async def get_prediction(image: UploadFile, training_paths: list[str], nu: float = 0.4, kernel: str = "rbf"):
    training_paths = set(training_paths[0].split(","))
    embedder = ImageEmbedder()
    hash_str = create_set_hash(training_paths)
    if active_embeddings.get(hash_str, None) is None:
        active_embeddings[hash_str] = embedder(train_paths=training_paths)

    train_embeddings = active_embeddings.get(hash_str)
    test_embeddings = embedder(binary_image=image.file.read())

    ocsvm = OCSVMModel(nu=nu, kernel=kernel)
    ocsvm.train(train_embeddings)
    predictions = ocsvm.predict(test_embeddings)
    return {"prediction": True if int(predictions[0]) == 1 else False}
