from PIL import Image
import os


def resize_image(input_path, output_path):
    # Open the image
    original_image = Image.open(input_path)

    # Create a new image with dimensions 768x768 and fill with white
    new_size = (768, 768)
    new_image = Image.new("RGB", new_size, "white")

    # Paste the original image onto the new image with center alignment
    offset = ((new_size[0] - original_image.width) // 2, (new_size[1] - original_image.height) // 2)
    new_image.paste(original_image, offset)

    # Resize the image to 512x512
    resized_image = new_image.resize((512, 512))

    # Save the resized image as PNG
    resized_image.save(output_path, "PNG")


if __name__ == "__main__":
    # Get input image path
    input_image_path = input("Enter the path of the input image (.ppm format): ").strip()

    # Check if the file exists
    if not os.path.exists(input_image_path):
        print("Error: The specified file does not exist.")
    else:
        # Create output path with the same name and PNG extension
        output_image_path = os.path.splitext(input_image_path)[0] + "_resized.png"

        # Perform the resizing and saving
        resize_image(input_image_path, output_image_path)
        print(f"Image resized and saved to {output_image_path}")
