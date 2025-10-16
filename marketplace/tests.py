import datetime as dt

import pytest
from chalk.client import ChalkClient
from chalk.features import DataFrame

from src.marketplace import (
    Review,
    User,
)


@pytest.fixture(scope="session")
def client():
    return ChalkClient(branch=True)


def test_user_aggregations(client: ChalkClient) -> None:
    now = dt.datetime.now()
    client.check(
        input={
            User.id: 1,
            User.reviews: DataFrame(
                [
                    Review(
                        id=1,
                        star_rating=3,
                        created_at=now - dt.timedelta(days=1),
                    ),
                    Review(
                        id=2,
                        star_rating=4,
                        created_at=now - dt.timedelta(days=2),
                    ),
                    Review(
                        id=3,
                        star_rating=2,
                        created_at=now - dt.timedelta(days=3),
                    ),
                    Review(
                        id=4,
                        star_rating=3,
                        created_at=now - dt.timedelta(days=4),
                    ),
                    Review(
                        id=5,
                        star_rating=3,
                        created_at=now - dt.timedelta(days=5),
                    ),
                    Review(
                        id=6,
                        star_rating=1,
                        created_at=now - dt.timedelta(days=6),
                    ),
                    Review(
                        id=7,
                        star_rating=5,
                        created_at=now - dt.timedelta(days=7),
                    ),
                    Review(
                        id=8,
                        star_rating=2,
                        created_at=now - dt.timedelta(days=8),
                    ),
                    Review(
                        id=9,
                        star_rating=3,
                        created_at=now - dt.timedelta(days=9),
                    ),
                ],
            ),
        },
        assertions={
            User.review_count["3d"]: 3,
            User.review_count["7d"]: 7,
            User.average_rating_given["3d"]: 3,
            User.average_rating_given["7d"]: 3,
        },
    )
