import io

import requests
from bs4 import BeautifulSoup
from cairosvg import svg2png
from chalk import online
from chalk.features import DataFrame, Features
from PIL import Image as PI

from src.feature_sets import Image, Website


@online
def get_html(url: Website.url) -> Website.html:
    """Get the HTML of a website."""
    res = requests.get(url)
    return res.content


def process_url(image_src, host):
    if image_src.startswith("https://") or image_src.startswith("http://"):
        return image_src
    elif image_src.startswith("//"):
        return f"https:{image_src}"
    return f"https://{host}/{image_src.strip('/')}"


@online
def get_images(
    html: Website.html, website_url: Website.url, website_host: Website.host
) -> Website.images[Image.url, Image.source_url]:
    """Extract all images from the HTML of a website."""
    soup = BeautifulSoup(html, "html.parser")

    return DataFrame(
        [
            Image(
                url=process_url(it["src"], website_host),
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
    image_bytes: Image.image_bytes, image_type: Image.type
) -> Features[Image.x, Image.y]:
    """Read the image using pillow and get its dimensions"""
    pil_bytes = io.BytesIO()
    if image_type == "svg":
        svg2png(bytestring=image_bytes, write_to=pil_bytes)
    else:
        pil_bytes.write(image_bytes)
    x, y = PI.open(pil_bytes).size
    return Image(x=x, y=y)
