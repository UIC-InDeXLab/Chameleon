import os

import requests


class Connector:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_binary_data(self, url):
        r = requests.get(self.base_url + url)
        return r.content

    def post_files(self, url, files, params=None):
        r = requests.post(self.base_url + url, files=files, headers={'accept': 'application/json'}, params=params)
        return r.content

    def get_json_data(self, url):
        r = requests.get(self.base_url + url)
        return r.json()


class ImageAnalyzerConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("IMAGE_ANALYZER_BASE_URL"))

    def get_random_image_from_pattern(self, pattern: str):
        return self.get_binary_data(f"/v1/images/pattern/{pattern}")

    def get_pattern_details(self, pattern: str):
        return self.get_json_data(f"/v1/prompt/{pattern}")


class ImageEditorConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("IMAGE_EDITOR_BASE_URL"))

    def generate_new_image(self, base_image, mask, prompt, size="256x256", n=1):
        files = {
            'image': base_image,
            'mask': mask,
        }
        params = {
            'prompt': prompt,
            'n': str(n),
            'size': size,
        }
        return self.post_files("/v1/images/edits", files=files, params=params)


class MaskGeneratorConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("MASK_GENERATOR_BASE_URL"))

    def get_mask(self, image):
        files = {
            'image': image,
        }
        return self.post_files("/v1/images/masks", files=files)
