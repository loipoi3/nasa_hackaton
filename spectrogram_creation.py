import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

pd.set_option('display.max_columns', None)

# Load the catalog
loaded_cat = pd.read_hdf(r'D:\nasa_hackaton\data\processed_data\lunar_training.h5', key='catalog_data')

# Directory to save spectrograms
saved_dir = 'output_spectrogram'  # Update with the directory where you want to save the spectrograms
os.makedirs(saved_dir, exist_ok=True)

# Loop through the catalog to create and save spectrograms for each event
for index, row in loaded_cat.iterrows():
    event_time = row['np_time_rel(sec)']
    event_velocity = row['np_velocity(m/s)']
    event_start_time = row['time_rel(sec)']  # Extract the start time from time_rel column

    # Convert lists to numpy arrays
    time_array = np.array(event_time)
    velocity_array = np.array(event_velocity)

    # Check if both arrays are not empty and have at least two points for computing the sampling frequency
    if len(time_array) > 1 and len(velocity_array) > 1:
        if len(time_array) == len(velocity_array):
            # Create the spectrogram
            try:
                f, t, Sxx = spectrogram(velocity_array,
                                        fs=1 / (time_array[1] - time_array[0]))  # fs is the sampling frequency

                # Plot and save the spectrogram
                plt.figure(figsize=(10, 6))
                plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
                plt.ylabel('Frequency [Hz]')
                plt.xlabel('Time [s]')
                plt.title(f'Spectrogram of Seismic Event {index}')
                plt.colorbar(label='Power/Frequency (dB/Hz)')

                # Add a vertical red line where the true signal starts (using time_rel value)
                plt.axvline(x=event_start_time, color='red', linestyle='--', linewidth=2, label="Signal Start")

                # Find the index in the `t` array that corresponds to the event_start_time
                start_time_index = np.argmin(np.abs(t - event_start_time))

                # Find the frequency with the maximum power at the start time index
                max_freq_index = np.argmax(Sxx[:, start_time_index])
                max_frequency = f[max_freq_index]
                print(f"Max frequency at start time: {max_frequency} Hz")

                # Plot a vertical bar at the maximum frequency at the start time
                plt.scatter(event_start_time, max_frequency, color='blue', marker='o', s=100,
                            label=f"Max Frequency at Start Time: {max_frequency:.2f} Hz")
                plt.axhline(y=max_frequency, color='blue', linestyle='--', linewidth=2)

                # Find the maximum energy (power) across the entire time and frequency
                max_energy = 0
                max_freq_idx = 0
                max_time_idx = 0
                for freq_idx, freq in enumerate(Sxx):
                    for time_idx, energy in enumerate(freq):
                        if energy > max_energy:
                            max_energy = energy
                            max_freq_idx = freq_idx
                            max_time_idx = time_idx

                # Find the corresponding time and frequency of the maximum power
                global_max_time = t[max_time_idx]
                global_max_frequency = f[max_freq_idx]
                print(f"Max frequency over entire event: {global_max_frequency} Hz at time {global_max_time} s")

                # Plot a marker and horizontal line for the maximum frequency over the entire time
                plt.scatter(global_max_time, global_max_frequency, color='green', marker='x', s=100,
                            label=f"Global Max Frequency: {global_max_frequency:.2f} Hz")
                plt.axhline(y=global_max_frequency, color='green', linestyle='--', linewidth=2)

                # Add a legend with the frequencies labeled
                plt.legend(loc='upper left')

                # Save the spectrogram using the filename in the file name
                plt.savefig(f"{saved_dir}/spectrogram_event_{index}.png")
                plt.close()
            except Exception as e:
                print(f"Error creating spectrogram for event {index}: {e}")
        else:
            print(f"Error: Time and velocity arrays for event {index} are not the same length.")
    else:
        print(f"Error: Insufficient data for event {index}. Time or velocity array is too short.")
