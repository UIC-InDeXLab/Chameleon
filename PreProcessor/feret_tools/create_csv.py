import os
import csv


def read_metadata(metadata_path):
    # Read metadata from the given file path
    metadata = {}
    with open(metadata_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            metadata[key.strip()] = value.strip()
    return metadata


def create_csv(image_directory, ground_truth_directory, csv_filename):
    # Open the CSV file for writing
    with open(csv_filename, 'w', newline='') as csv_file:
        # Define the CSV columns
        fieldnames = ['filename', 'gender', 'yob', 'race']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Iterate through image directory
        for image_filename in os.listdir(image_directory):
            if image_filename.lower().endswith('.png'):
                # Extract person_id from the image filename
                person_id, _ = os.path.splitext(image_filename)[0].split('_', 1)

                # Construct the path to the corresponding text file in the ground truth directory
                metadata_path = os.path.join(ground_truth_directory, person_id, f'{person_id}.txt')

                # Check if the corresponding text file exists
                if os.path.exists(metadata_path):
                    # Read metadata from the text file
                    metadata = read_metadata(metadata_path)

                    # Write a row to the CSV file
                    writer.writerow({
                        'filename': image_filename,
                        'gender': metadata.get('gender', ''),
                        'yob': metadata.get('yob', ''),
                        'race': metadata.get('race', '')
                    })


if __name__ == "__main__":
    # Specify the paths to the image directory, ground truth directory, and CSV filename
    image_directory = input("Enter the path to the image directory: ").strip()
    ground_truth_directory = input("Enter the path to the ground truth directory: ").strip()
    csv_filename = input("Enter the desired CSV filename (e.g., output.csv): ").strip()

    # Create the CSV file
    create_csv(image_directory, ground_truth_directory, csv_filename)
    print(f"CSV file '{csv_filename}' created successfully.")
