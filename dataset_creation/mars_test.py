import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Base directory where the Mars test unprocessed_data files are located
base_directory = '../unprocessed_data/mars/test/unprocessed_data' #insert your own path

# Directory where the output HDF5 file will be saved
output_directory = './processed_data' #insert your own path

# Name of the output HDF5 file
output_filename = 'mars_lunar_test.h5'

# Function to process all CSV files in a given folder
def process_files_in_folder(folder_path):
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

                # Extract 'rel_time(sec)' and 'velocity(c/s)' columns as numpy arrays
                time_rel = mini_dataset['rel_time(sec)'].values
                velocity = mini_dataset['velocity(c/s)'].values

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
    output_file = os.path.join(output_directory, output_filename)

    # Save the DataFrame to an HDF5 file
    folder_dataset.to_hdf(output_file, key='processed_data', mode='w')
    print(f'File saved successfully: {output_file}')

# Process the files in the base directory
process_files_in_folder(base_directory)