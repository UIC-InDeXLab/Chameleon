import io

from PIL import Image, ImageDraw


def find_unused_color(image):
    img = Image.open(io.BytesIO(image)).convert("RGBA")

    width, height = img.size

    existing_colors = set()

    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))
            existing_colors.add((r, g, b))

    unused_color = None
    for r in range(256):
        for g in range(256):
            for b in range(256):
                if (r, g, b) not in existing_colors:
                    unused_color = (r, g, b)
                    break
            if unused_color:
                break
        if unused_color:
            break

    return unused_color


def draw_circle_around_transparent_pixels(image):
    unused_color = find_unused_color(image)
    img = Image.open(io.BytesIO(image)).convert("RGBA")

    width, height = img.size
    circle_radius = int(0.1 * width)
    draw = ImageDraw.Draw(img)

    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))

            circle_x, circle_y = x, y

            circle_bbox = (
                circle_x - circle_radius,
                circle_y - circle_radius,
                circle_x + circle_radius,
                circle_y + circle_radius
            )

            if a == 0:
                draw.ellipse(circle_bbox, width=circle_radius, fill=unused_color, outline=unused_color)

    result_img = Image.new("RGBA", (width, height))

    unused_r, unused_g, unused_b = unused_color

    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))

            if r == unused_r and g == unused_g and b == unused_b:
                result_img.putpixel((x, y), (r, g, b, 0))
            else:
                result_img.putpixel((x, y), (r, g, b, a))

    output_buffer = io.BytesIO()
    result_img.save(output_buffer, format="PNG")
    binary_data = output_buffer.getvalue()
    return binary_data
