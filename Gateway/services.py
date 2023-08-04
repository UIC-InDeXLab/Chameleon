from models import MUP
from connectors import ImageAnalyzerConnector, MaskGeneratorConnector, ImageEditorConnector

import requests


def get_pattern_details(pattern: str) -> (int, str):
    connector = ImageAnalyzerConnector()
    details = connector.get_pattern_details(pattern=pattern)
    return int(details["count"]), str(details["prompt"])


def get_mup_random_image(mup: MUP):
    pattern = mup.generate_similar_pattern()
    mup.chosen_similar_pattern = pattern
    connector = ImageAnalyzerConnector()
    image = connector.get_random_image_from_pattern(pattern)
    return image


def get_mask(base_image):
    connector = MaskGeneratorConnector()
    return connector.get_mask(base_image)


def generate_image_by_prompt(base_image, mask, prompt, size="256x256", n=1):
    connector = ImageEditorConnector()
    return connector.generate_new_image(base_image, mask, prompt, size, n)


def get_image_from_url(url):
    return requests.get(url).content
