import json
import os

from models import MUPEncoder


def store_png_files(dir, png_files_names, png_binaries):
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


def load_image(filename, parent_ds, is_generated: bool):
    # TODO: Duplicate logic with get_image API,
    #       needs to be merged with get_image API as a core functionality that provides image data

    path = os.getenv("RESOURCES_PATH") if not is_generated else os.getenv("GENERATION_PATH")
    with open(os.path.join(path, parent_ds, filename), "rb") as f:
        data = f.read()

    return data


def convert_list_to_dict(l: list) -> dict:
    q = {}
    if l is None:
        return q

    for i in l:
        k, v = i.split("=")
        q[k] = int(v)
    return q
