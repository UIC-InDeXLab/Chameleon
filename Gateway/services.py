import random

import requests

from connectors import ImageAnalyzerConnector, MaskGeneratorConnector, ImageEditorConnector
from models import MaximalUncoveredPattern, Pattern


def get_pattern_details(pattern: str) -> (int, str):
    connector = ImageAnalyzerConnector()
    details = connector.get_pattern_details(pattern=pattern)
    return int(details["count"]), str(details["prompt"])


def get_mup_random_image(mup: MaximalUncoveredPattern):
    similar_patterns = get_similar_patterns(mup)
    choice: Pattern = random.choices(similar_patterns, weights=[sp.frequency for sp in similar_patterns])[0]
    mup.chosen_similar_pattern = choice
    connector = ImageAnalyzerConnector()
    image = connector.get_random_image_from_pattern(choice.pattern)
    return image


def get_similar_patterns(mup: MaximalUncoveredPattern) -> list[Pattern]:
    similar_patterns: list[Pattern] = []
    for p in mup.similar_patterns_strings:
        frequency, prompt = get_pattern_details(p)
        similar_patterns.append(Pattern(p, frequency, prompt))

    return similar_patterns


def get_mask(base_image):
    connector = MaskGeneratorConnector()
    return connector.get_mask(base_image)


def generate_image_by_prompt(base_image, mask, prompt, size="256x256", n=1):
    connector = ImageEditorConnector()
    return connector.generate_new_image(base_image, mask, prompt, size, n)


def get_image_from_url(url):
    return requests.get(url).content
