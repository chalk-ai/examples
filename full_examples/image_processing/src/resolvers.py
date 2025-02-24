import io

import requests
from bs4 import BeautifulSoup
from chalk import online
from chalk.features import DataFrame, Features
from PIL import Image as PI

from src.feature_sets import Image, Website


@online
def get_html(url: Website.url) -> Website.html:
    """Get the HTML of a website."""
    res = requests.get(url)
    return res.content


@online
def get_images(
    html: Website.html, website_url: Website.url
) -> Website.images[Image.url, Image.source_url]:
    """Extract all images from the HTML of a website."""
    soup = BeautifulSoup(html, "html.parser")

    return DataFrame(
        [
            Image(
                url=it["src"]
                if it["src"].startswith("https://") or it["src"].startswith("http://")
                else f"{website_url}/{it['src']}",
                source_url=website_url,
            )
            for it in soup.find_all("img")
        ]
    )


@online
def get_image_bytes(
    image_url: Image.url,
) -> Image.image_bytes:
    """Get the image as bytes from the image's URL."""
    res = requests.get(image_url)
    return res.content


@online
def get_image_shape(
    image_bytes: Image.image_bytes,
) -> Features[Image.x, Image.y]:
    """Read the image using pillow and get its dimensions"""
    x, y = PI.open(io.BytesIO(image_bytes)).size
    return Image(x=x, y=y)
