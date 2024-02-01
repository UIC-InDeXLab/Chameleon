import json
from json import JSONEncoder
from typing import List


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


class Pattern:
    def __init__(self, pattern: str, frequency: int, prompt: str, attributes: List[Attribute]):
        self.pattern = pattern
        self.frequency = frequency
        self.prompt = prompt
        self.attributes = attributes

    def get_attribute_by_name(self, name):
        for a in self.attributes:
            if a.name == name:
                return a
        return None

    def get_attribute_by_pattern_index(self, index):
        for a in self.attributes:
            if a.pattern_index == index:
                return a
        return None

    def convert_pattern_to_filters(self, pattern: str):
        filters = {}
        for i, c in enumerate(list(pattern)):
            if str(c).lower() == "x":
                continue
            filters[self.get_attribute_by_pattern_index(i).name] = int(c)

        return filters

    def substitute_one_attribute_value(self, attribute_index, val):
        return self.pattern[:attribute_index] + str(val) + self.pattern[attribute_index + 1:]

    @property
    def num_attributes(self):
        return len(self.attributes)

    @property
    def cardinality_of_attributes(self):
        return [a.cardinality for a in self.attributes]

    @property
    def attributes_ids(self):
        return [a.column_number for a in self.attributes]


class MaximalUncoveredPattern(Pattern):
    def __init__(self, pattern: str, frequency: int, prompt: str, attributes):
        super().__init__(pattern, frequency, prompt, attributes)
        self.chosen_similar_pattern: Pattern | None = None
        self.generated_images = []
        self.pulled_arms = []

    def add_image(self, path: str):
        self.generated_images.append(path)

    def is_satisfied(self, threshold: int):
        return threshold <= len(self.generated_images) + self.frequency

    def get_count_needed(self, threshold: int):
        return threshold - len(self.generated_images) - self.frequency

    @property
    def similar_patterns_strings(self) -> list[str]:
        patterns = []
        for i, c in enumerate(list(self.pattern)):
            attr = self.get_attribute_by_pattern_index(i)
            if attr.ordered:
                start = int(c) - 1 if int(c) > 0 else 0
                end = int(c) + 1 if int(c) < attr.cardinality - 1 else int(c)
                patterns.extend(
                    [self.substitute_one_attribute_value(i, index) for index in range(start, end + 1)])
            else:
                patterns.extend([self.substitute_one_attribute_value(i, index) for index in range(attr.cardinality)])

        return [p for p in patterns if p != self.pattern]


class MUPEncoder(JSONEncoder):
    def default(self, o: MaximalUncoveredPattern):
        return {"pattern": o.pattern, "frequency": o.frequency, "prompt": o.prompt,
                "generation_pattern": json.dumps(o.chosen_similar_pattern, cls=PatternEncoder)}


class PatternEncoder(JSONEncoder):
    def default(self, o: Pattern):
        return {"pattern": o.pattern, "frequency": o.frequency, "prompt": o.prompt}
