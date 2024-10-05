import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import gaussian_filter1d


# Function to compute spectral flux
def compute_spectral_flux(signal, fs, window_size, hop_size, smooth=True):
    num_windows = max(1, (len(signal) - window_size) // hop_size)
    spectral_flux = np.zeros(num_windows)
    time_vals = np.zeros(num_windows)

    for i in range(num_windows):
        start = i * hop_size
        end = start + window_size
        windowed_signal = signal[start:end]
        spectrum = np.abs(fft(windowed_signal))
        if i > 0:
            spectral_flux[i] = np.sum((spectrum - prev_spectrum) ** 2)
        prev_spectrum = spectrum
        time_vals[i] = start / fs  # Time in seconds

    if smooth:
        spectral_flux = gaussian_filter1d(spectral_flux, sigma=2)

    return spectral_flux, time_vals


# Function to apply Butterworth low-pass filter
def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def plot_and_save_onsets(signal, time_vals, spectral_flux, onset_time, filename):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot the original signal (time-domain) on the left y-axis
    ax1.plot(time_vals, signal, label="Time-Domain Signal", color='b')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_title('Time-Domain Signal with Spectral Flux and Detected Onset')

    # Plot the spectral flux on the right y-axis
    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
    ax2.plot(time_vals[:len(spectral_flux)], spectral_flux, label="Spectral Flux", color='g', alpha=0.7)
    ax2.set_ylabel('Spectral Flux', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Add red line for the detected onset
    if onset_time is not None:
        ax1.axvline(x=onset_time, color='red', linestyle='--', label='Detected Onset')

    fig.tight_layout()  # To prevent overlap of labels
    plt.legend(loc="upper right")
    plt.savefig(filename)
    plt.close()



def save_image_truth(csv_times, csv_data, line_time, output_image_path):
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(csv_times, csv_data, label='Velocity (m/s)')
    plt.axvline(x=line_time, color='r', linestyle='--', label='Event Time')  # Highlight the event time
    plt.title(f'Time Domain Plot')
    plt.xlabel('Time (sec)')
    plt.ylabel('Velocity (m/s)')
    plt.legend()

    # Save the plot as an image
    plt.savefig(output_image_path)
    plt.close()  # Close the figure to avoid display overlap

def detect_signal_end(spectral_flux, time_vals, start_idx, end_threshold=1e-16):
    for i in range(start_idx, len(spectral_flux)):
        if spectral_flux[i] < end_threshold:
            return time_vals[i]
    return None


def create_samples(loaded_cat, output_path):
    for index, row in loaded_cat.iterrows():
        csv_times = np.array(row['np_time_rel(sec)'])
        csv_data = np.array(row['np_velocity(m/s)'])
        line_time = row['time_rel(sec)']
        evid = row['evid']
        evid_dir = os.path.join(output_path, evid)
        evid_image_truth = os.path.join(evid_dir, f'{evid}_TRUTH.png')
        create_dir(evid_dir)
        save_image_truth(csv_times, csv_data, line_time, output_image_path=evid_image_truth)


    for index, row in loaded_cat.iterrows():
        csv_times = np.array(row['np_time_rel(sec)'])
        csv_data = np.array(row['np_velocity(m/s)'])
        line_time = row['time_rel(sec)']
        evid = row['evid']
        evid_dir = os.path.join(output_path, evid)
        evid_image_truth = os.path.join(evid_dir, f'{evid}_TRUTH.png')
        create_dir(evid_dir)
        save_image_truth(csv_times, csv_data, line_time, output_image_path=evid_image_truth)

        # Ensure we have enough data points in csv_times
        if len(csv_times) > 1 and len(csv_data) > 1:
            fs = 1 / (csv_times[1] - csv_times[0])

            # Compute spectral flux directly on the raw signal (without filtering)
            window_size = max(1, int(0.5 * fs))  # Ensure non-zero window size
            hop_size = max(1, int(0.1 * fs))  # Ensure non-zero hop size

            spectral_flux, time_vals = compute_spectral_flux(csv_data, fs, window_size, hop_size)
            onset_indices = find_peaks(spectral_flux, height=1e-16, distance=50)[0]
            onset_times = time_vals[onset_indices]

            if len(onset_times) > 0:
                signal_start_time = onset_times[0]
                print(f"Signal detected starting at {signal_start_time} seconds.")
            else:
                signal_start_time = None
                print("No significant onset detected.")

            plot_and_save_onsets(csv_data, csv_times, spectral_flux, signal_start_time,
                                 os.path.join(evid_dir, f'{evid}_PREDICTED.png'))


        else:
            print(f"Skipping row {index} due to insufficient data.")


saved_dir = r'output'
loaded_cat = pd.read_hdf(r'C:\Users\User\PycharmProjects\NASA\lunar_training.h5', key='catalog_data')
os.makedirs(saved_dir, exist_ok=True)
print(loaded_cat.head(5))
create_samples(loaded_cat, output_path=saved_dir)
