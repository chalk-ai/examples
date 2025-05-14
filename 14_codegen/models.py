import chalk.functions as F
from chalk import _
from chalk.features import features
from custom_model import CustomModel


@features
class User:
    id: int
    name: str
    email: str
    name_match_score: float = F.jaccard_similarity(_.email, _.name)
    score1: float
    score2: float


model1 = CustomModel(
    url="https://internal.example.com/model1",
    dependencies={
        "nms": User.name_match_score,
        "email": User.email,
    },
    computes=User.score1,
)

model2 = CustomModel(
    url="https://internal.example.com/model2",
    dependencies={
        "nms": User.name_match_score,
        "email": User.email,
    },
    computes=User.score2,
)


if __name__ == "__main__":
    CustomModel.render_all(
        header="from models import *",
        path="./score_resolvers.py",
        models=[model1, model2],
    )
