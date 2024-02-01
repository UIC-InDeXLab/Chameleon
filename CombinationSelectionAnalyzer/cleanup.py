import pandas as pd


def clean_csv(input_filename, output_filename):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_filename)

    # Convert "l2r" column to string to handle both numeric and string values
    df['l2r'] = df['l2r'].astype(str)

    # Group by "l2r" and keep only the first and last rows for each group
    grouped_df = df.groupby('l2r', as_index=False)
    cleaned_df = pd.concat([grouped_df.head(1), grouped_df.tail(1)])

    # Sort the DataFrame by the original index to preserve the original order
    cleaned_df.sort_index(inplace=True)

    # Write the cleaned DataFrame to a new CSV file
    cleaned_df.to_csv(output_filename, index=False)


# Example usage
if __name__ == "__main__":
    fname = "mingap_l2_350-r.csv"
    input_filename = fname  # Replace with your input CSV file
    output_filename = fname.replace(".csv", "") + "-digest.csv" # Replace with your desired output CSV file

    clean_csv(input_filename, output_filename)
