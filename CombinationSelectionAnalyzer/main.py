from fastapi import FastAPI
from connectors import ImageAnalyzerConnector
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()
app = FastAPI()


def get_levels_dict_from_patterns(patterns):
    mups_level_dict = {}
    for pattern in patterns:
        v = mups_level_dict.setdefault(3 - pattern.count("x"), [])
        v.append(pattern)
    return mups_level_dict


@app.post("/v1/simulate/{strategy}/")
def simulate(strategy: str, dataset_id: str, threshold: int, resolve_until_level: int = 2):
    strategies_dict = {"greedy": handle_greedy, "random": handle_random, "bestcomb": handle_best_combination,
                       "mingap": handle_min_gap}
    strategies_dict.get(strategy.lower())(dataset_id, threshold, resolve_until_level)


def handle_greedy(dataset_id: str, threshold: int, resolve_until_level: int = 2):
    mups = []
    connector = ImageAnalyzerConnector()
    time = datetime.now()
    fname = f"greedy_l{resolve_until_level}_{threshold}_{time}.csv"
    total = 1
    with open(fname, 'a') as f:
        f.write("total,l1,l2,l3\n")

    while True:
        res = dict(connector.get_mups(dataset_id, threshold))
        best_combination = list(res["best_mups"].keys())[0]
        count_needed = threshold - int(res["best_mups"].get(best_combination)["count"])
        patterns = list(res["mups"].keys())
        levels_dict = get_levels_dict_from_patterns(patterns)
        if len(levels_dict.get(resolve_until_level, [])) == 0:
            break

        connector.create_fake_images(dataset_id, age_group=list(best_combination)[0],
                                     gender=list(best_combination)[1],
                                     race=list(best_combination)[2],
                                     count=count_needed)
        with open(fname, 'a') as f:
            for i in range(count_needed):
                f.write(
                    f"{total},{len(levels_dict.get(1, []))},{len(levels_dict.get(2, []))},{len(levels_dict.get(3, []))}\n")
                total += 1


def handle_random(dataset_id: str, threshold: int, resolve_until_level: int = 2):
    mups = []
    connector = ImageAnalyzerConnector()
    time = datetime.now()
    fname = f"random_l{resolve_until_level}_{threshold}_{time}.csv"
    total = 1
    with open(fname, 'a') as f:
        f.write("total,l1,l2,l3\n")

    while True:
        res = dict(connector.get_mups(dataset_id, threshold))
        patterns = list(res["mups"].keys())
        levels_dict = get_levels_dict_from_patterns(patterns)
        best_combination = list(res["best_mups"].keys())[0]
        count_needed = threshold - int(res["best_mups"].get(best_combination)["count"])
        if len(levels_dict.get(resolve_until_level, [])) == 0:
            break

        with open(fname, 'a') as f:
            for i in range(count_needed):
                age_group = str(random.randint(0, 7))
                gender = str(random.randint(0, 1))
                race = str(random.randint(0, 3))
                connector.create_fake_images(dataset_id, age_group=age_group, gender=gender, race=race,
                                             count=1)
                f.write(
                    f"{total},{len(levels_dict.get(1, []))},{len(levels_dict.get(2, []))},{len(levels_dict.get(3, []))}\n")
                total += 1


def handle_best_combination(dataset_id: str, threshold: int, resolve_until_level: int = 2):
    mups = []
    connector = ImageAnalyzerConnector()
    time = datetime.now()
    fname = f"bestcomb_l{resolve_until_level}_{threshold}_{time}.csv"
    total = 1
    with open(fname, 'a') as f:
        f.write("total,l1,l2,l3\n")

    while True:
        res = dict(connector.get_mups(dataset_id, threshold))
        patterns = list(res["mups"].keys())
        levels_dict = get_levels_dict_from_patterns(patterns)
        if len(levels_dict.get(resolve_until_level, [])) == 0:
            break

        combinations = dict(connector.get_combinations_status(dataset_id))
        best_combination_candidates = [(combination, count) for combination, count in combinations.items() if
                                       int(count) < threshold]
        best_combination, count = max(best_combination_candidates, key=lambda x: x[1])
        count_needed = threshold - count

        age_group = list(best_combination)[0]
        gender = list(best_combination)[1]
        race = list(best_combination)[2]
        connector.create_fake_images(dataset_id, age_group=age_group, gender=gender, race=race,
                                     count=count_needed)

        with open(fname, 'a') as f:
            for i in range(count_needed):
                f.write(
                    f"{total},{len(levels_dict.get(1, []))},{len(levels_dict.get(2, []))},{len(levels_dict.get(3, []))}\n")
                total += 1


def handle_min_gap(dataset_id: str, threshold: int, resolve_until_level: int = 2):
    mups = []
    connector = ImageAnalyzerConnector()
    time = datetime.now()
    fname = f"mingap_l{resolve_until_level}_{threshold}_{time}.csv"
    total = 1
    with open(fname, 'a') as f:
        f.write("total,l1,l2,l3\n")

    while True:
        res = dict(connector.get_mups(dataset_id, threshold))
        patterns = list(res["mups"].keys())
        levels_dict = get_levels_dict_from_patterns(patterns)
        if len(levels_dict.get(resolve_until_level, [])) == 0:
            break

        min_mup = [(pattern, int(details["count"])) for pattern, details in res["mups"].items() if
                   int(details["count"]) < threshold]

        best_pattern, count = max(min_mup, key=lambda x: x[1])
        count_needed = threshold - count
        print(best_pattern)
        age_group = list(best_pattern)[0] if str(list(best_pattern)[0]).lower() != 'x' else str(random.randint(0, 7))
        gender = list(best_pattern)[1] if str(list(best_pattern)[1]).lower() != 'x' else str(random.randint(0, 1))
        race = list(best_pattern)[2] if str(list(best_pattern)[2]).lower() != 'x' else str(random.randint(0, 3))
        connector.create_fake_images(dataset_id, age_group=age_group, gender=gender, race=race,
                                     count=count_needed)

        with open(fname, 'a') as f:
            for i in range(count_needed):
                f.write(
                    f"{total},{len(levels_dict.get(1, []))},{len(levels_dict.get(2, []))},{len(levels_dict.get(3, []))}\n")
                total += 1
