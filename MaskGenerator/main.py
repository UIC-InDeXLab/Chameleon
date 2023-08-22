import enum

from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from rembg.bg import remove

import brush_remover
import square_remover

app = FastAPI()

class AccuracyLevel(enum.Enum):
    ACCURATE = "accurate"
    MODERATE = "moderate"
    IMPRECISE = "imprecise"


@app.post("/v1/images/masks")
async def generate_mask(image: UploadFile, accuracy_level: AccuracyLevel = AccuracyLevel.ACCURATE):
    import invert_remover
    base = remove(image.file.read(), alpha_matting=True)

    if accuracy_level == AccuracyLevel.MODERATE:
        output = brush_remover.draw_circle_around_transparent_pixels(base)
    elif accuracy_level == AccuracyLevel.IMPRECISE:
        output = square_remover.find_transparent_bounding_box(base)
    else:
        output = base

    return Response(content=output, media_type="image/png")
