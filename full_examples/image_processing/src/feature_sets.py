import chalk.functions as F
from chalk.features import DataFrame, Primary, _, feature, features


@features
class Image:
    url: Primary[str]

    # The website that the image was scraped from.
    source_url: "Website.url"

    # The raw bytes of the image
    image_bytes: bytes

    # The x dimension for an image
    x: int

    # The y dimension for an image
    y: int

    # whether the image is flaged based on an in house model running deployed on the
    # `image-model_1.0.1_2024-09-16` SageMaker endpoint.
    flagged: bool = feature(
        max_staleness="infinity",
        underscore=F.sagemaker_predict(
            _.image_bytes, endpoint="image-model_1.0.1_2024-09-16"
        ),
    )


@features
class Website:
    url: Primary[str]

    # The html of the website
    html: str

    # The images associated with a given website
    images: DataFrame[Image]
