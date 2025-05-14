import requests
from chalk import online
from models import *


@online
def get_score1(nms: User.name_match_score, email: User.email) -> User.score1:
    response = requests.post(
        "https://internal.example.com/model1",
        headers={"accept": "application/json"},
        json={"nms": nms, "email": email},
    )
    return response.json().get("prediction")


@online
def get_score2(nms: User.name_match_score, email: User.email) -> User.score2:
    response = requests.post(
        "https://internal.example.com/model2",
        headers={"accept": "application/json"},
        json={"nms": nms, "email": email},
    )
    return response.json().get("prediction")
