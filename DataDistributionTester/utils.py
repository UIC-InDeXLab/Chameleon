import os
import requests
from pathlib import Path
from hashlib import sha256


def download_embedder():
    embedder_url = os.getenv("EMBEDDER_URL")
    embedder_file_path = Path("embedder.tflite")

    if not embedder_file_path.exists():
        try:
            response = requests.get(embedder_url, stream=True)
            response.raise_for_status()

            with open(embedder_file_path, 'wb') as embedder_file:
                for chunk in response.iter_content(chunk_size=8192):
                    embedder_file.write(chunk)

        except requests.RequestException as e:
            raise FileNotFoundError(f"Failed to download embedder file. Error: {e}")

    return embedder_file_path


def get_image_paths(directory):
    image_paths = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more extensions if needed

    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            image_paths.append(os.path.join(directory, filename))

    return image_paths


def create_set_hash(data_set):
    sorted_elements = sorted(data_set)  # Ensure consistent order
    concatenated_string = ''.join(str(x) for x in sorted_elements)
    return sha256(concatenated_string.encode('utf-8')).hexdigest()
