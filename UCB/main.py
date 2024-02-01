import json
import pickle

from fastapi import FastAPI, Depends
from ucb import UCB

app = FastAPI()
gucb: UCB = None


@app.on_event("shutdown")
def shutdown_event():
    global gucb
    with open("ucb.pkl", "wb") as file:
        pickle.dump(gucb, file)


@app.on_event("startup")
def startup_event():
    global gucb
    try:
        with open("ucb.pkl", "rb") as file:
            gucb = pickle.load(file)
        print("Object loaded successfully:", gucb)
    except FileNotFoundError:
        print("No serialized object found. Using default object.")


def get_ucb():
    global gucb

    if gucb is None:
        with open("config.json", 'r') as f:
            config = json.load(f)

        gucb = UCB(config.get("num_arms"), config.get("num_combinations"))

    return gucb


@app.get("/v1/ucb/arms/")
def get_arm(input_combination: int, ucb=Depends(get_ucb)):
    arm = ucb.choose_arm(input_combination)
    print(f"chosen arm is {arm}")
    return {"arm": arm}


@app.post("/v1/ucb/arms/")
def update_arm(arm: str, combination: int, reward: int, ucb=Depends(get_ucb)):
    ucb.update(int(arm), int(combination), reward)
    return {"success": True}
