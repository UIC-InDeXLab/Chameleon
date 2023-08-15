import enum

from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from rembg.bg import remove

import brush_remover
import square_remover

app = FastAPI()

class MaskLevel(enum.Enum):
    ACCURATE = "rembg"
    MODERATE = "brush"
    LOOSE = "square"


@app.post("/v1/images/masks")
async def generate_mask(image: UploadFile, mask_type: MaskLevel = MaskLevel.ACCURATE):
    import invert_remover
    base = remove(image.file.read(), alpha_matting=True)

    if mask_type == MaskLevel.MODERATE:
        output = brush_remover.draw_circle_around_transparent_pixels(base)
    elif mask_type == MaskLevel.LOOSE:
        output = square_remover.find_transparent_bounding_box(base)
    else:
        output = base

    return Response(content=output, media_type="image/png")
