import os.path
import subprocess

import pandas as pd

import utils


def get_images(ds_id: str, skip: int = 0, limit: int = None, filters=None, is_generated: bool | None = None,
               order_by=None, random_choose=False) -> pd.DataFrame:
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))
    if filters is None:
        filters = {}

    if is_generated is not None:
        filters["is_generated"] = is_generated

    for column, value in filters.items():
        df = df[df[column] == value]

    if order_by:
        df = df.sort_values(by=order_by)

    if random_choose:
        df = df.sample(n=limit)

    if limit is None:
        df = df.iloc[skip:]
    else:
        df = df.iloc[skip:skip + limit]

    return df


def get_image(ds_id, filename):
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))
    df = df[df["filename"] == filename]
    return df.iloc[0]


def get_random_image(ds_id, filters=None, is_generated: bool | None = None):
    return get_images(ds_id=ds_id, filters=filters, is_generated=is_generated, random_choose=True, limit=1).iloc[0]


def get_random_images(ds_id, filters=None, is_generated: bool | None = None, limit: int = 1):
    return get_images(ds_id=ds_id, filters=filters, random_choose=True, is_generated=is_generated, limit=limit)


def get_images_count(ds_id, filters=None, is_generated: bool | None = None):
    return len(get_images(ds_id=ds_id, filters=filters, is_generated=is_generated))


def add_image(ds_id, filename: str, attributes: dict, is_generated):
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))
    attributes['filename'] = filename
    attributes['is_generated'] = is_generated
    df.loc[len(df)] = attributes
    df.to_csv(os.path.join("./datasets", ds_id + ".csv"), index=False)


def get_partial_table_df(ds_id, filters=None, limit: int = 1):
    return get_random_images(ds_id=ds_id, filters=filters, limit=limit)


def get_mups(ds_id, threshold, dimension, cardinality_of_attributes, chosen_attributes_ids):
    count = get_images_count(ds_id)
    envs = {
        "DIMENSION": dimension,
        "COUNT": count,
        "THRESHOLD": threshold,
        "CARDINALITIES": "_".join([str(i) for i in cardinality_of_attributes]),
        "ATTRIBUTES": "_".join([str(i) for i in chosen_attributes_ids]),
        "FILE": f"/datasets/{ds_id}.csv"
    }
    cmd = f"""docker run --rm -v ./datasets/:/datasets/ -e {"-e ".join([f"{k}={v} " for k, v in envs.items()])} --ulimit nofile=122880:122880 {utils.assert_env_var_not_none('MUP_DOCKER_IMAGE')}"""
    print(f"{cmd=}")
    output = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, text=True).stdout
    start, end = False, False
    mups = []
    for l in output.splitlines():
        if "-" * 50 in l:
            if not start:
                start = True
            else:
                end = True
        elif start and not end:
            mups.append(l)
    return mups
