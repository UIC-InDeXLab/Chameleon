from singleton import Singleton


class Attribute:
    def __init__(self, name: str, cardinality: int, ordered: bool, position: int, column_number: int,
                 pattern_index: int, mapping: dict):
        self.column_number = column_number
        self.name = name
        self.cardinality = cardinality
        self.ordered = ordered
        self.mapping = mapping
        self.position = position
        self.pattern_index = pattern_index


class Dataset:
    def __init__(self, name, resource_path, csv_path, attributes, prompt_prefix, prompt_suffix):
        self.name = name
        self.__resource_path__ = resource_path
        self.__csv_path__ = csv_path
        self.attributes = [Attribute(**a) for a in attributes]
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix

    def get_attribute_by_name(self, name):
        for a in self.attributes:
            if a.name == name:
                return a
        return None

    def get_attribute_by_column_number(self, col_name):
        for a in self.attributes:
            if a.column_number == col_name:
                return a
        return None

    def get_prompt(self, filters: dict):
        atts = []
        for k, v in filters.items():
            a = self.get_attribute_by_name(k)
            atts.append((a.position, a.mapping.get(str(v))))

        atts = sorted(atts, key=lambda x: x[0])
        return self.prompt_prefix + " " + " ".join([a[1] for a in atts]) + " " + self.prompt_suffix

    @property
    def num_attributes(self):
        return len(self.attributes)

    @property
    def cardinality_of_attributes(self):
        return [a.cardinality for a in self.attributes]

    @property
    def attributes_ids(self):
        return [a.column_number for a in self.attributes]


@Singleton
class DatasetManager:
    def __init__(self):
        self.datasets = []

    def add_dataset(self, ds: Dataset):
        self.datasets.append(ds)

    def get_dataset(self) -> Dataset:
        return self.datasets[0]
