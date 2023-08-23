import random

import requests

import connectors
from connectors import ImageAnalyzerConnector, MaskGeneratorConnector, ImageEditorConnector
from models import MaximalUncoveredPattern, Pattern


def get_pattern_details(dataset_id: str, pattern: str) -> (int, str):
    connector = ImageAnalyzerConnector()
    details = connector.get_pattern_details(dataset_id=dataset_id, pattern=pattern)
    return int(details["count"]), str(details["prompt"])


def get_image_details(dataset_id: str, filename: str):
    connector = ImageAnalyzerConnector()
    return connector.get_image_details(dataset_id, filename)


def get_mup_similar_image(dataset_id: str, mup: MaximalUncoveredPattern):
    similar_patterns = get_similar_patterns(dataset_id, mup)
    choice: Pattern = random.choices(similar_patterns, weights=[sp.frequency for sp in similar_patterns])[0]
    mup.chosen_similar_pattern = choice
    connector = ImageAnalyzerConnector()
    return connector.get_random_image_from_pattern(dataset_id=dataset_id, pattern=choice.pattern)


def get_random_image(dataset_id: str):
    connector = ImageAnalyzerConnector()
    return connector.get_random_image_from_dataset(dataset_id=dataset_id)


def get_similar_patterns(dataset_id: str, mup: MaximalUncoveredPattern) -> list[Pattern]:
    similar_patterns: list[Pattern] = []
    for p in mup.similar_patterns_strings:
        frequency, prompt = get_pattern_details(dataset_id, p)
        similar_patterns.append(Pattern(p, frequency, prompt))

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
    res = connector.get_mups(dataset_id, threshold)
    best_mups = res["best_mups"]
    mups = res["mups"]
    return best_mups, mups


def get_mups_patterns(dataset_id: str, threshold: int):
    connector = connectors.ImageAnalyzerConnector()
    mups: list[str] = connector.get_mups(dataset_id, threshold)["mups"]
    return mups


def add_image_to_dataset(dataset_id: str, file_name: str):
    connector = connectors.ImageAnalyzerConnector()
    return connector.create_image(dataset_id, file_name)
