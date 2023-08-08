import os.path

import pandas as pd

from models import Gender, Race, AgeGroup


def get_images(ds_id: str, skip: int = 0, limit: int = None,
               gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
               order_by=None, random_choose=False) -> pd.DataFrame:
    filters = {k: v for k, v in (('gender', gender), ('race', race), ('age_group', age_group)) if v is not None}
    filters = {k: v.value for k, v in filters.items()}
    df = pd.read_csv(os.path.join("./datasets", ds_id + ".csv"))

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


def get_random_image(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None):
    return get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group,
                      random_choose=True, limit=1).iloc[0]


def get_random_images(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None,
                      limit: int = 1):
    return get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group, random_choose=True, limit=limit)


def get_images_count(ds_id, gender: Gender = None, race: Race = None, age_group: AgeGroup = None):
    return len(get_images(ds_id=ds_id, gender=gender, race=race, age_group=age_group))
