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

    def get_json_data(self, url, params=None):
        r = requests.get(self.base_url + url, params=params)
        return r.json()

    def post_form_data(self, url, params):
        r = requests.post(self.base_url + url, params=params,
                          headers={'accept': 'application/json',
                                   'content-type': 'application/x-www-form-urlencoded'})
        return r.json()

    def post_json_data(self, url, json):
        r = requests.post(self.base_url + url, json=json, headers={'accept': 'application/json',
                                                                   'content-type': 'application/json'})
        return r.json()


class ImageAnalyzerConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("IMAGE_ANALYZER_BASE_URL"))

    def get_random_image_from_dataset(self, dataset_id: str, filters: dict = None, include_generated_image=None):
        if filters is None:
            filters = {}
        params = {"include_generated_images": include_generated_image,
                  "filters": [f"{k}={v}" for k, v in filters.items()]}

        return self.get_json_data(f"/v1/datasets/{dataset_id}/images/random/", params=params)

    def get_image_details(self, dataset_id: str, filename: str):
        return self.get_json_data(f"/v1/datasets/{dataset_id}/images/{filename}/details/")

    def get_images_details(self, dataset_id: str, filters: dict = None, include_generated_images: bool = True):
        params = {"filters": [f"{k}={v}" for k, v in filters.items() if filters is not None],
                  "include_generated_images": include_generated_images}
        return self.get_json_data(f"/v1/datasets/{dataset_id}/images/prompt/", params=params)

    def get_dataset_details(self, dataset_id: str):
        return self.get_json_data(f"/v1/datasets/{dataset_id}/images/count/")

    def get_dataset_images(self, dataset_id: str, skip=0, limit=None, filters: dict = None, is_generated=None):
        params = {"skip": skip, "limit": limit,
                  "filters": [f"{k}={v}" for k, v in filters.items() if filters is not None],
                  "is_generated": is_generated}
        return self.get_json_data(f"/v1/datasets/{dataset_id}/images/", params=params)

    def create_partial_ds(self, json):
        return self.post_json_data("/v1/images/export/partial/", json=json)

    def get_mups(self, dataset_id: str, threshold: int):
        params = {"threshold": threshold}
        return self.get_json_data(f"/v1/datasets/{dataset_id}/mups/", params=params)

    def create_image(self, dataset_id: str, filename: str, attributes: dict = None):
        if attributes is None:
            filters = {}
        params = {"attributes": [f"{k}={v}" for k, v in attributes.items()]}
        return self.post_form_data(f"/v1/datasets/{filename}/", params=params)

    def get_current_main_dataset(self):
        return self.get_json_data(f"/v1/datasets/details/")


class ImageEditorConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("IMAGE_EDITOR_BASE_URL"))

    def edit_image(self, base_image, mask, prompt, size="256x256", n=1):
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

    def generate_image(self, prompt: str, size="256x256", n=1):
        params = {
            'prompt': prompt,
            'n': str(n),
            'size': size
        }
        return self.post_form_data("/v1/images/generations", params=params)


class MaskGeneratorConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("MASK_GENERATOR_BASE_URL"))

    def get_mask(self, image, accuracy_level):
        files = {
            'image': image,
        }
        params = {
            'accuracy_level': accuracy_level,
        }
        return self.post_files("/v1/images/masks", files=files, params=params)


class UCBConnector(Connector):
    def __init__(self):
        super().__init__(os.getenv("UCB_BASE_URL"))

    def get_arm(self, input_combination: int):
        params = {"input_combination": input_combination}
        return self.get_json_data("/v1/ucb/arms/", params=params)

    def update_arm(self, arm: str, combination: int, reward: int):
        params = {"arm": arm, "combination": combination, "reward": reward}
        return self.post_form_data("/v1/ucb/arms/", params=params)
