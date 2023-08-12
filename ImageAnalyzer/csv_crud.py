import os.path
import subprocess

import pandas as pd

import utils
from models import Gender, Race, AgeGroup


def get_images(ds_id: str, skip: int = 0, limit: int = None,
               gender: Gender = None, race: Race = None, age_group: AgeGroup = None, is_generated: bool | None = None,
               order_by=None, random_choose=False) -> pd.DataFrame:
    filters = {k: v for k, v in (('gender', gender), ('race', race), ('age_group', age_group)) if v is not None}
    filters = {k: v.value for k, v in filters.items()}
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))

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


def get_random_image(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                     is_generated: bool | None = None):
    return get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group, is_generated=is_generated,
                      random_choose=True, limit=1).iloc[0]


def get_random_images(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                      is_generated: bool | None = None, limit: int = 1):
    return get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group, random_choose=True,
                      is_generated=is_generated, limit=limit)


def get_images_count(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                     is_generated: bool | None = None):
    return len(get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group, is_generated=is_generated))


def add_image(ds_id, filename: str, gender: Gender, race: Race, age_group: AgeGroup, is_generated):
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))
    df.loc[len(df)] = {'filename': filename, 'gender': gender, 'race': race, 'age_group': age_group,
                       'is_generated': is_generated}
    df.to_csv(os.path.join("./datasets", ds_id + ".csv"), index=False)


def get_mups(ds_id, threshold):
    count = get_images_count(ds_id)
    cmd = f"""docker run --rm -v ./datasets/:/datasets/ -e DIMENSION=3 -e COUNT={count} -e THRESHOLD={threshold} -e FILE=/datasets/{ds_id}.csv --ulimit nofile=122880:122880 {utils.assert_env_var_not_none('MUP_DOCKER_IMAGE')}"""
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
