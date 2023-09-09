import random
from typing import List

import requests

import connectors
from connectors import ImageAnalyzerConnector, MaskGeneratorConnector, ImageEditorConnector
from models import MaximalUncoveredPattern, Pattern, Attribute


def get_image_details(dataset_id: str, filename: str):
    connector = ImageAnalyzerConnector()
    return connector.get_image_details(dataset_id, filename)


def get_dataset_images(dataset_id: str, skip=0, limit=None, filters: dict = None, is_generated=None):
    connector = ImageAnalyzerConnector()
    return connector.get_dataset_images(dataset_id, skip, limit, filters=filters, is_generated=is_generated)


def get_mup_similar_image(dataset_id: str, mup: MaximalUncoveredPattern):
    similar_patterns = get_similar_patterns(dataset_id, mup)
    choice: Pattern = random.choices(similar_patterns, weights=[sp.frequency for sp in similar_patterns])[0]
    mup.chosen_similar_pattern = choice
    connector = ImageAnalyzerConnector()
    res = connector.get_random_image_from_dataset(dataset_id=dataset_id,
                                                  filters=mup.convert_pattern_to_filters(choice.pattern))
    return res


def get_random_image(dataset_id: str):
    connector = ImageAnalyzerConnector()
    return connector.get_random_image_from_dataset(dataset_id=dataset_id)


def get_similar_patterns(dataset_id: str, mup: MaximalUncoveredPattern) -> list[Pattern]:
    similar_patterns: list[Pattern] = []
    connector = ImageAnalyzerConnector()
    for p in mup.similar_patterns_strings:
        res = connector.get_images_details(dataset_id, mup.convert_pattern_to_filters(p))
        similar_patterns.append(Pattern(p, res["count"], res["prompt"], mup.attributes))

    return similar_patterns


def get_mask(base_image, accuracy_level: str):
    connector = MaskGeneratorConnector()
    return connector.get_mask(base_image, accuracy_level)


def edit_image(base_image, mask, prompt, size="256x256", n=1):
    connector = ImageEditorConnector()
    return connector.edit_image(base_image, mask, prompt, size, n)


def generate_image(prompt, size="256x256", n=1):
    connector = ImageEditorConnector()
    return connector.generate_image(prompt, size=size, n=n)


def get_image_from_url(url):
    return requests.get(url).content


def get_dataset_details(dataset_id: str):
    connector = ImageAnalyzerConnector()
    return connector.get_dataset_details(dataset_id=dataset_id)


def create_partial_ds(data):
    connector = ImageAnalyzerConnector()
    return connector.create_partial_ds(data)


def get_mups_details(dataset_id: str, threshold: int):
    connector = connectors.ImageAnalyzerConnector()
    return connector.get_mups(dataset_id, threshold)


def add_image_to_dataset(dataset_id: str, file_name: str, pattern:str, attributes: List[Attribute] = None):
    connector = connectors.ImageAnalyzerConnector()
    p = Pattern(pattern, 0, "", attributes)
    return connector.create_image(dataset_id, file_name, p.convert_pattern_to_filters(pattern))


def get_current_main_dataset():
    connector = connectors.ImageAnalyzerConnector()
    return connector.get_current_main_dataset()
