import json
from json import JSONEncoder


class Pattern:
    def __init__(self, pattern: str, frequency: int, prompt: str):
        self.pattern = pattern
        self.frequency = frequency
        self.prompt = prompt

    @property
    def age_group(self):
        return int(list(self.pattern)[0])

    @property
    def gender(self):
        return int(list(self.pattern)[1])

    @property
    def race(self):
        return int(list(self.pattern)[2])


class MaximalUncoveredPattern(Pattern):
    def __init__(self, pattern: str, frequency: int, prompt: str):
        super().__init__(pattern, frequency, prompt)
        self.chosen_similar_pattern: Pattern | None = None
        self.generated_images = []

    def add_image(self, path: str):
        self.generated_images.append(path)

    def is_satisfied(self, threshold: int):
        return threshold <= len(self.generated_images) + self.frequency

    def get_count_needed(self, threshold: int):
        return threshold - len(self.generated_images) - self.frequency

    @property
    def similar_races(self):
        choices = list(range(0, 4))
        choices.remove(self.race)
        return choices

    @property
    def similar_genders(self):
        return [1] if self.gender == 0 else [0]

    @property
    def similar_age_groups(self):
        if self.age_group == 0:
            return [1]
        elif self.age_group == 8:
            return [7]
        else:
            return [self.age_group - 1, self.age_group + 1]

    @property
    def similar_patterns_strings(self) -> list[str]:
        patterns = []
        for a in self.similar_age_groups:
            patterns.append("".join([str(a), str(self.gender), str(self.race)]))

        for g in self.similar_genders:
            patterns.append("".join([str(self.age_group), str(g), str(self.race)]))

        for r in self.similar_races:
            patterns.append("".join([str(self.age_group), str(self.gender), str(r)]))

        return patterns


class MUPEncoder(JSONEncoder):
    def default(self, o: MaximalUncoveredPattern):
        return {"pattern": o.pattern, "frequency": o.frequency, "prompt": o.prompt,
                "generation_pattern": json.dumps(o.chosen_similar_pattern, cls=PatternEncoder)}


class PatternEncoder(JSONEncoder):
    def default(self, o: Pattern):
        return {"pattern": o.pattern, "frequency": o.frequency, "prompt": o.prompt}
