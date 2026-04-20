import logging

import chalkcompute

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# In production, swap microsoft/resnet-50 for a fine-tuned content moderation model.
# The pipeline structure is identical — only the model name changes.
MODEL_NAME = "microsoft/resnet-50"


@chalkcompute.function(
    name="classify-image",
    image=(
        chalkcompute.Image.debian_slim()
        .run_commands("pip install torch --index-url https://download.pytorch.org/whl/cpu")
        .pip_install(["transformers", "Pillow", "requests"])
    ),
)
def classify_image(image_url: str) -> str:
    """Download an image by URL and classify it inside an isolated container.

    Untrusted image bytes are fetched and processed entirely within the
    sandbox — the caller never handles raw upload data.

    Returns a JSON string with the top-5 labels and the most-confident one.
    Threshold/branching logic lives in the Temporal workflow, not here.
    """
    import io
    import json

    import requests
    from PIL import Image
    from transformers import pipeline

    log.info("Downloading image: %s", image_url)
    resp = requests.get(image_url, timeout=30, headers={"User-Agent": "ChalkModeration/1.0"})
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))

    log.info("Classifying with %s", MODEL_NAME)
    classifier = pipeline("image-classification", model=MODEL_NAME)
    results = classifier(img, top_k=5)

    labels = [{"label": r["label"], "confidence": round(r["score"], 4)} for r in results]
    top = labels[0]

    return json.dumps({
        "labels": labels,
        "top_label": top["label"],
        "top_confidence": top["confidence"],
    })
