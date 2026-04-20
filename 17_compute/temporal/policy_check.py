import logging

import chalkcompute

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

MODEL_NAME = "openai/clip-vit-base-patch32"

# Each policy is scored by softmax-ing its prompt against a diverse set of
# benign POSITIVE alternatives. This works around CLIP's well-known weakness
# with negation: "no children" gets ignored by the encoder, whereas "a photo
# of an animal" is a real competing concept that wins for benign images.
#
# Score for a policy = P(policy prompt | {policy prompt, ...benign alternatives}).
# Scores are independent across policies and need NOT sum to 1.
POLICY_PROMPTS = {
    "violence": "a photo depicting violence or graphic injury",
    "adult": "a photo with adult or sexual content",
    "weapon": "a photo prominently showing a weapon",
    "minor": "a photo showing a human child",
}

BENIGN_ALTERNATIVES = [
    "a photo of an animal",
    "a photo of a landscape or nature scene",
    "a photo of food",
    "a photo of everyday household objects",
    "a photo of an adult person",
    "a peaceful, safe-for-work scene",
]


@chalkcompute.function(
    name="policy-check",
    image=(
        chalkcompute.Image.debian_slim()
        .run_commands("pip install torch --index-url https://download.pytorch.org/whl/cpu")
        .pip_install(["transformers", "Pillow", "requests"])
    ),
)
def policy_check(image_url: str) -> str:
    """Score an image against policies using CLIP positive-vs-benigns softmax.

    Stage 2 of the moderation pipeline. Runs only when stage-1 confidence is
    borderline — see workflow.py for the branching logic.

    Returns JSON: {policy_scores: {name: p}, max_policy, max_score}. Each p is
    an independent probability in [0, 1]; they do not have to sum to 1.
    """
    import io
    import json

    import requests
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor

    log.info("Downloading image: %s", image_url)
    resp = requests.get(image_url, timeout=30, headers={"User-Agent": "ChalkModeration/1.0"})
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")

    log.info("Loading CLIP %s", MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)

    keys = list(POLICY_PROMPTS.keys())
    n_options = 1 + len(BENIGN_ALTERNATIVES)

    # One forward pass over all prompt groups; reshape afterwards.
    flat_prompts: list[str] = []
    for k in keys:
        flat_prompts.append(POLICY_PROMPTS[k])
        flat_prompts.extend(BENIGN_ALTERNATIVES)

    log.info("Scoring %d policies vs %d benign alternatives", len(keys), len(BENIGN_ALTERNATIVES))
    inputs = processor(text=flat_prompts, images=img, return_tensors="pt", padding=True)
    logits = model(**inputs).logits_per_image                   # (1, len(keys) * n_options)
    grouped = logits.view(len(keys), n_options)                 # (policies, [pos, benigns...])
    probs = grouped.softmax(dim=-1)                             # per-policy softmax
    scores = probs[:, 0].tolist()                               # P(positive) per policy

    policy_scores = {k: round(float(s), 4) for k, s in zip(keys, scores)}
    max_policy = max(policy_scores, key=policy_scores.__getitem__)

    return json.dumps({
        "policy_scores": policy_scores,
        "max_policy": max_policy,
        "max_score": policy_scores[max_policy],
    })
