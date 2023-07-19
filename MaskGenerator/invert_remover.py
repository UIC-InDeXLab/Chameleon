import numpy as np
import rembg
from PIL import Image
from PIL.Image import Image as PILImage
from pymatting import estimate_alpha_cf, estimate_foreground_ml, stack_images
from scipy.ndimage import binary_erosion


def _alpha_matting_cutout(
        img: PILImage,
        mask: PILImage,
        foreground_threshold: int,
        background_threshold: int,
        erode_structure_size: int, ) -> PILImage:
    if img.mode == "RGBA" or img.mode == "CMYK":
        img = img.convert("RGB")

    img = np.asarray(img)
    mask = np.asarray(mask)

    is_foreground = mask > foreground_threshold
    is_background = mask < background_threshold

    structure = None
    if erode_structure_size > 0:
        structure = np.ones(
            (erode_structure_size, erode_structure_size), dtype=np.uint8
        )

    is_foreground = binary_erosion(is_foreground, structure=structure)
    is_background = binary_erosion(is_background, structure=structure, border_value=1)

    trimap = np.full(mask.shape, dtype=np.uint8, fill_value=128)
    trimap[is_foreground] = 0
    trimap[is_background] = 255

    img_normalized = img / 255.0
    trimap_normalized = trimap / 255.0

    alpha = estimate_alpha_cf(img_normalized, trimap_normalized)
    foreground = estimate_foreground_ml(img_normalized, alpha)
    cutout = stack_images(foreground, alpha)

    cutout = np.clip(cutout * 255, 0, 255).astype(np.uint8)
    cutout = Image.fromarray(cutout)

    return cutout


rembg.bg.alpha_matting_cutout = _alpha_matting_cutout
