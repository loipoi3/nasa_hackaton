import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Base directory where the test unprocessed_data folders are located
base_directory = '../unprocessed_data/lunar/test/unprocessed_data/' #insert your own path

# Directory where the output HDF5 files will be saved
output_directory = './processed_data/' #insert your own path

# Function to process each folder and its CSV files
def process_folder(folder_path, folder_name):
    # Initialize lists to store filenames, time, and velocity unprocessed_data
    filenames = []
    time_rel_list = []
    velocity_list = []

    # Loop through each file in the folder
    for file in os.listdir(folder_path):
        # Check if the file is a CSV file
        if file.endswith('.csv'):
            # Form the full path to the CSV file
            file_path = os.path.join(folder_path, file)

            try:
                # Read the CSV file into a pandas DataFrame
                mini_dataset = pd.read_csv(file_path)

                # Extract 'time_rel(sec)' and 'velocity(m/s)' columns as numpy arrays
                time_rel = mini_dataset['time_rel(sec)'].values
                velocity = mini_dataset['velocity(m/s)'].values

            except KeyError:
                # If the required columns are not found, use empty arrays
                time_rel = np.array([])
                velocity = np.array([])

            # Append the filename and extracted unprocessed_data to the lists
            filenames.append(file)
            time_rel_list.append(time_rel)
            velocity_list.append(velocity)

    # Create a DataFrame from the accumulated unprocessed_data
    folder_dataset = pd.DataFrame({
        'filename': filenames,
        'time_rel(sec)': time_rel_list,
        'velocity(m/s)': velocity_list
    })

    # Define the path for the output HDF5 file
    output_file = os.path.join(output_directory, f'{folder_name}_lunar_test.h5')

    # Save the DataFrame to an HDF5 file
    folder_dataset.to_hdf(output_file, key='processed_data', mode='w')
    print(f'File saved successfully: {output_file}')


# Loop through all items in the base directory
for folder in os.listdir(base_directory):
    folder_path = os.path.join(base_directory, folder)
    # Check if the current item is a directory
    if os.path.isdir(folder_path):
        # Process the folder by calling the process_folder function
        process_folder(folder_path, folder)