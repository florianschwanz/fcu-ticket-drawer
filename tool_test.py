import glob
import os
from pathlib import Path

import cv2
import pytest

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

image_path = os.path.join(script_path, "tmp", "canvas-stadium.png")
templates_dir = os.path.join(script_path, "templates", "blocks")

MATCH_THRESHOLD = 0.95


def get_template_files():
    if not os.path.exists(templates_dir):
        return []
    return glob.glob(os.path.join(templates_dir, "*.png"))


@pytest.fixture(scope="module")
def canvas_gray():
    if not os.path.exists(image_path):
        pytest.fail(f"Canvas image not found: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        pytest.fail(f"Failed to load canvas image: {image_path}")

    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


@pytest.mark.parametrize("template_path", get_template_files())
def test_template_is_found(canvas_gray, template_path: Path):
    """
    For every file in templates/, check if it exists in the canvas
    with at least 95% confidence.
    """

    # Load template in grayscale
    template = cv2.imread(template_path)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    if template is None:
        pytest.fail(f"Could not load template: {template_path}")

    # Check Dimensions
    h, w = template.shape
    c_h, c_w = canvas_gray.shape
    if h > c_h or w > c_w:
        pytest.fail(
            f"Template {template_path} is larger than the canvas! ({w}x{h} vs {c_w}x{c_h})"
        )

    # Perform Match
    res = cv2.matchTemplate(canvas_gray, template, cv2.TM_CCOEFF_NORMED)

    # Get the best match score
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Assert
    error_msg = (
        f"Template '{os.path.basename(template_path)}' not found! "
        f"Score: {max_val:.2f} (Threshold: {MATCH_THRESHOLD})"
    )
    assert max_val >= MATCH_THRESHOLD, error_msg
