import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Define the path to the Mars InSight training catalog CSV file
cat_file = '../data/unprocessed_data/mars/training/catalogs/Mars_InSight_training_catalog_final.csv'  # insert your own path

# Read the catalog CSV file into a pandas DataFrame
cat = pd.read_csv(cat_file)

# Define the directory where the training unprocessed_data files are located
data_directory = '../unprocessed_data/mars/training/unprocessed_data/'  # insert your own path

# Initialize lists to store the time and velocity unprocessed_data from each CSV file
csv_times_list = []
csv_data_list = []

# Loop through each row in the catalog DataFrame
for index, row in cat.iterrows():
    # Get the filename from the current row of the catalog
    test_filename = row['filename']

    # Form the full path to the corresponding unprocessed_data CSV file
    csv_file = os.path.join(data_directory, f'{test_filename}')
    print(csv_file)  # Output the file path for debugging

    # Check if the unprocessed_data CSV file exists
    if os.path.exists(csv_file):
        # Read the unprocessed_data CSV into a pandas DataFrame
        data_cat = pd.read_csv(csv_file)

        # Extract the 'rel_time(sec)' and 'velocity(c/s)' columns as numpy arrays
        csv_times = data_cat['rel_time(sec)'].values
        csv_data = data_cat['velocity(c/s)'].values

        # Append the extracted arrays to the corresponding lists
        csv_times_list.append(csv_times)
        csv_data_list.append(csv_data)
    else:
        # If the file does not exist, append empty numpy arrays
        csv_times_list.append(np.array([]))
        csv_data_list.append(np.array([]))

# Add the time and velocity unprocessed_data lists as new columns in the catalog DataFrame
cat['np_time_rel(sec)'] = csv_times_list
cat['np_velocity(m/s)'] = csv_data_list

# Define the path where the updated DataFrame will be saved as an HDF5 file
h5_file_path = '../data/processed_data/mars/train/mars_training.h5'  # insert your own path

# Save the DataFrame to an HDF5 file
cat.to_hdf(h5_file_path, key='mars_training', mode='w')