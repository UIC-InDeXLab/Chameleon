import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from sklearn.svm import OneClassSVM


class ImageEmbedder:
    def __init__(self, model_path='embedder.tflite', l2_normalize=True, quantize=True):
        base_options = python.BaseOptions(model_asset_path=model_path)
        self.options = vision.ImageEmbedderOptions(
            base_options=base_options, l2_normalize=l2_normalize, quantize=quantize)

    def __call__(self, train_paths=None, binary_image=None, temp_image_path="temp_image.png", *args, **kwargs):
        def create_embeddings(paths):
            embeddings = {}
            with vision.ImageEmbedder.create_from_options(self.options) as embedder:
                for path in paths:
                    try:
                        img = mp.Image.create_from_file(path)
                        embeddings[path] = embedder.embed(img)
                    except Exception as e:
                        print(f"an error occured while embedding {path}, {e}")
                        continue
            return embeddings

        if train_paths is not None:
            embeddings = create_embeddings(train_paths)
        elif binary_image is not None:
            with open(temp_image_path, "wb") as temp_image:
                temp_image.write(binary_image)
            embeddings = create_embeddings([temp_image_path])
        else:
            raise RuntimeError("You should provide either binary image or train paths")

        return [v.embeddings[0].embedding for k, v in embeddings.items()]


class OCSVMModel:
    def __init__(self, nu, kernel):
        self.nu = nu
        self.kernel = kernel
        self.ocsvm = None

    def train(self, embeddings):
        self.ocsvm = OneClassSVM(nu=self.nu, kernel=self.kernel).fit(embeddings)

    def predict(self, embeddings):
        if self.ocsvm is None:
            raise RuntimeError("model not found, you have to call train method first")
        return self.ocsvm.predict(embeddings)
