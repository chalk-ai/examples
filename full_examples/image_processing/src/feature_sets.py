import datetime as dt

import chalk.functions as F
from chalk.features import DataFrame, _, feature, features
from pydantic import BaseModel

@features
class Website:
    url: str
    image_urls: list[str]
    html: str
    images: DataFrame[Image]


@features
class Image:
    url: str
    image_bytes: bytes
    x: int
    y: int
    flagged: bool = feature(
        max_staleness="infinity", underscore=F.sagemaker_predict(_.image_bytes)
    )
