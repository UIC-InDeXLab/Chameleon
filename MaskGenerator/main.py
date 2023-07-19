from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from rembg.bg import remove

app = FastAPI()


@app.post("/v1/images/masks")
async def generate_mask(image: UploadFile):
    import invert_remover
    output = remove(image.file.read(), alpha_matting=True)
    return Response(content=output, media_type="image/png")
