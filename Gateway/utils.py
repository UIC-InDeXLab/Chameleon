import json
import os

from models import MUPEncoder


def store_png_files(png_files_names, png_binaries, dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

    for name, bin in zip(png_files_names, png_binaries):
        with open(os.path.join(dir, name), "wb") as f:
            f.write(bin)


def store_mup(mup, filename, dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

    with open(os.path.join(dir, filename), "w") as f:
        f.write(json.dumps(mup, cls=MUPEncoder))


def load_image(filename, is_generated: bool):
    path = os.getenv("RESOURCES_PATH") if not is_generated else os.getenv("GENERATION_PATH")
    with open(os.path.join(path, filename), "rb") as f:
        data = f.read()

    return data
