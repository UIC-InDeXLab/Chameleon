import random
from json import JSONEncoder


class MUP:
    _weights = None

    @property
    def weights(self):
        return type(self)._weights

    @weights.setter
    def weights(self, weights):
        if type(self)._weights is None:
            type(self)._weights = weights

    def __init__(self, pattern: str, count: int, prompt: str):
        self.pattern = pattern
        self.count = count
        self.prompt = prompt
        self.chosen_similar_pattern = None
        self.generated_images = []

    def generate_similar_pattern(self):
        def get_new_age_group(age_group):
            if age_group == 0:
                return 1
            elif age_group == 8:
                return 7
            else:
                return age_group + random.choice([-1, 1])

        def get_new_gender(gender):
            return 1 if gender == 0 else 0

        def get_new_race(race):
            choices = list(range(0, 4))
            choices.remove(race)
            return random.choice(choices)

        age_group, gender, race = [int(i) for i in list(self.pattern)]
        choice: int = random.choices([0, 1, 2], weights=self.weights)[0]
        if choice == 0:
            age_group = get_new_age_group(age_group)
        if choice == 1:
            gender = get_new_gender(gender)
        if choice == 2:
            race = get_new_race(race)

        return "".join([str(age_group), str(gender), str(race)])

    def add_image(self, path: str):
        self.generated_images.append(path)

    def is_satisfied(self, threshold: int):
        return threshold <= len(self.generated_images) + self.count

    def get_count_needed(self, threshold: int):
        return threshold - len(self.generated_images) - self.count


class MUPEncoder(JSONEncoder):
    def default(self, o: MUP):
        return {"pattern": o.pattern, "count": o.count, "prompt": o.prompt,
                "generation_pattern": o.chosen_similar_pattern}