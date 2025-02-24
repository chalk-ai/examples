from src.resolvers import get_html, get_images


def test_website():
    res = get_html("https://www.google.com")
    get_images(res, "https://www.google.com")
    breakpoint()
