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

    def get_combinations_status(self, dataset_id: str):
        return self.get_json_data(f"/v1/combinations/datasets/{dataset_id}/status/")

    def create_fake_images(self, dataset_id: str, gender: str, race: str, age_group: str, count: int = 1):
        params = {"gender": gender, "race": race, "age_group": age_group, "count": count}
        self.post_form_data(f"/v1/images/datasets/{dataset_id}/random/", params=params)

    def get_mups(self, dataset_id: str, threshold: int):
        params = {"threshold": threshold}
        return self.get_json_data(f"/v1/datasets/{dataset_id}/mups/", params=params)
