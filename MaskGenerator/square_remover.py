import io

from PIL import ImageDraw, Image


def find_transparent_bounding_box(image):
    img = Image.open(io.BytesIO(image)).convert("RGBA")
    width, height = img.size

    min_x = width
    min_y = height
    max_x = 0
    max_y = 0

    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))

            if a == 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    draw = ImageDraw.Draw(img)
    draw.rectangle((min_x, min_y, max_x, max_y), outline=(0, 0, 0, 0), fill=(0, 0, 0, 0))

    output_buffer = io.BytesIO()
    img.save(output_buffer, format="PNG")
    binary_data = output_buffer.getvalue()
    return binary_data
