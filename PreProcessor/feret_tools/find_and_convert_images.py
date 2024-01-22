import os

from resize_image import resize_image


def find_and_convert_images(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has a .ppm extension and contains "fa" in its name
            if file.lower().endswith('.ppm') and 'fa' in file.lower():
                ppm_path = os.path.join(root, file)
                # Create output path with the same name and PNG extension
                png_path = os.path.splitext(ppm_path)[0] + "_converted.png"

                # Perform the conversion using the previous script
                resize_image(ppm_path, png_path)
                print(f"Image {ppm_path} converted and saved to {png_path}")


if __name__ == "__main__":
    # Get the directory path
    directory_path = input("Enter the directory path: ").strip()

    # Check if the directory exists
    if not os.path.exists(directory_path):
        print("Error: The specified directory does not exist.")
    else:
        # Find and convert images in the directory and its subdirectories
        find_and_convert_images(directory_path)
