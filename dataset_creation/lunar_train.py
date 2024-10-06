import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Define the directory where the catalog CSV file is located
cat_directory = '../unprocessed_data/lunar/training/catalogs/'  # insert your own path

# Combine the directory and the catalog filename to form the full path
cat_file = os.path.join(cat_directory, 'apollo12_catalog_GradeA_final.csv')

# Read the catalog CSV into a pandas DataFrame
df = pd.read_csv(cat_file)

# Define the directory where the related unprocessed_data files are located
data_directory = './unprocessed_data/lunar/training/unprocessed_data/S12_GradeA/'  # insert your own path

# Initialize lists to hold time and velocity unprocessed_data from the CSV files
csv_times_list = []
csv_data_list = []

# Loop through each row in the catalog DataFrame
for index, row in df.iterrows():
    # Get the filename from the current row of the catalog
    test_filename = row['filename']

    # Form the full path to the corresponding unprocessed_data CSV file
    csv_file = os.path.join(data_directory, f'{test_filename}.csv')

    # Check if the unprocessed_data CSV file exists
    if os.path.exists(csv_file):
        # Read the unprocessed_data CSV into a pandas DataFrame
        data_cat = pd.read_csv(csv_file)

        # Extract the 'time_rel(sec)' and 'velocity(m/s)' columns as numpy arrays
        csv_times = data_cat['time_rel(sec)'].values
        csv_data = data_cat['velocity(m/s)'].values

        # Append the extracted arrays to the corresponding lists
        csv_times_list.append(csv_times)
        csv_data_list.append(csv_data)
    else:
        # If the file does not exist, append empty numpy arrays
        csv_times_list.append(np.array([]))
        csv_data_list.append(np.array([]))

# Add the time and velocity unprocessed_data lists as new columns in the catalog DataFrame
df['np_time_rel(sec)'] = csv_times_list
df['np_velocity(m/s)'] = csv_data_list

# Define the path where the updated DataFrame will be saved as an HDF5 file
h5_file_path = '../data/processed_data/lunar/train/lunar_training.h5'

# Save the DataFrame to an HDF5 file
df.to_hdf(h5_file_path, key='catalog_data', mode='w')