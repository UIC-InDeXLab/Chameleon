import os
import shutil


def copy_last_image_per_person(directory):
    # Dictionary to store the last image path for each person_id
    last_images = {}

    # Traverse the directory and its subdirectories
    for person_id_dir in os.listdir(directory):
        person_id_path = os.path.join(directory, person_id_dir)

        if os.path.isdir(person_id_path):
            # Find all PNG files in the person_id directory
            png_files = [file for file in os.listdir(person_id_path) if file.lower().endswith('.png')]

            if png_files:
                # Choose the last PNG file in the list
                last_image_path = os.path.join(person_id_path, png_files[-1])

                # Extract name from the file path
                _, name = os.path.split(last_image_path)

                # Create the destination path with the new name
                destination_path = os.path.join(person_id_path, f"{name.split('.')[0]}_final.png")

                # Copy the image to the new destination
                shutil.copy(last_image_path, destination_path)
                print(f"Image {last_image_path} copied and saved to {destination_path}")


if __name__ == "__main__":
    # Get the directory path
    directory_path = input("Enter the directory path: ").strip()

    # Check if the directory exists
    if not os.path.exists(directory_path):
        print("Error: The specified directory does not exist.")
    else:
        # Copy the last image for each person_id in the directory
        copy_last_image_per_person(directory_path)
