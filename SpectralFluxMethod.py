import numpy as np
from scipy.fftpack import fft
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from Utils import SaveImages
from LowPassFilter import LPassFilter
import os
import pandas as pd
from datetime import timedelta

class SpectralFlux:
    def __init__(self, save_result_dir, data, landscape):
        """
        Initialize the SpectralFlux class.

        Args:
            save_result_dir (str): Directory to save the result images and files.
            data (pandas.DataFrame): DataFrame containing seismic data.
            landscape (str): Type of landscape, 'lunar' or 'mars'.
        """
        self.data = data
        self.save_result_dir = save_result_dir
        self.butter_bandpass_filter = LPassFilter()
        self.saver = SaveImages()
        self.landscape_cutoff_mapping = {'lunar': 1, 'mars': 2.19}
        self.cutoff = self.landscape_cutoff_mapping.get(landscape, None)

    def _compute_spectral_flux(self, signal, fs, window_size, hop_size, smooth=True):
        """
        Compute the spectral flux of the input signal.

        Args:
            signal (numpy.ndarray): The input signal array.
            fs (float): Sampling frequency.
            window_size (int): Size of the window for FFT.
            hop_size (int): Step size for the window.
            smooth (bool): Whether to smooth the spectral flux or not.

        Returns:
            tuple: Spectral flux array and corresponding time values.
        """
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

    def onset_detection(self):
        """
        Perform onset detection on the input seismic data.

        Iterates through each event in the data, applies a bandpass filter,
        computes the spectral flux, and detects signal onsets.

        Returns:
            pandas.DataFrame: DataFrame with detected onset times and other related information.
        """
        if self.cutoff is not None:
            onset_time_predicted = []
            onset_time_ground_truth = []
            audio_duration_list = []
            evid_list = []
            filename_list = []
            signal_start_time_list = []
            detection_times_abs_list = []
            detection_times_rel_list = []

            for index, row in self.data.iterrows():
                # Ensure all required columns are available
                csv_times = np.array(row['np_time_rel(sec)'])
                csv_data = np.array(row['np_velocity(m/s)'])

                # Check if csv_times and csv_data are non-empty
                if len(csv_times) == 0 or len(csv_data) == 0:
                    print(f"Skipping row {index} due to empty data arrays.")
                    continue
                csv_times = np.array(row['np_time_rel(sec)'])
                csv_data = np.array(row['np_velocity(m/s)'])
                line_time = row['time_rel(sec)']
                evid = row['evid']
                fname = row['filename']  # Use the 'filename' from the DataFrame
                starttime = pd.to_datetime(row['time_abs(%Y-%m-%dT%H:%M:%S.%f)'])  # Parse the absolute time

                evid_dir = os.path.join(self.save_result_dir, evid)
                evid_image_truth = os.path.join(evid_dir, f'{evid}_TRUTH.png')
                self.saver.create_dir(evid_dir)

                self.saver.save_image(csv_times, csv_data, line_time, output_image_path=evid_image_truth,
                                      color='red')
                audio_duration = csv_times[-1] - csv_times[0]

                # Ensure we have enough data points in csv_times
                if len(csv_times) > 1 and len(csv_data) > 1:
                    fs = 1 / (csv_times[1] - csv_times[0])

                    # Apply bandpass filter
                    try:
                        csv_data_filtered = self.butter_bandpass_filter.filtering(csv_data, self.cutoff, fs, order=4)
                    except ValueError as e:
                        print(f"Error in filtering data for event {evid}: {e}")
                        continue

                    # Compute spectral flux on the filtered signal
                    window_size = max(1, int(0.2 * fs))
                    hop_size = max(1, int(0.05 * fs))
                    spectral_flux, time_vals = self._compute_spectral_flux(csv_data_filtered, fs, window_size, hop_size)
                    height = 0.3 * np.max(spectral_flux)

                    min_time_between_peaks = 0.1  # 100 ms
                    distance = int(min_time_between_peaks * fs)
                    distance = max(1, distance)
                    onset_indices = find_peaks(spectral_flux, height=height, distance=distance)[0]
                    onset_times = time_vals[onset_indices]

                    if len(onset_times) > 0:
                        signal_start_time = onset_times[0]

                        # Use starttime + signal_start_time to calculate the absolute time
                        detection_time_abs = (starttime + timedelta(seconds=signal_start_time)).strftime(
                            '%Y-%m-%dT%H:%M:%S.%f')
                        detection_time_rel = signal_start_time
                        print(f"Signal detected starting at {signal_start_time} seconds for event {evid}.")
                    else:
                        signal_start_time = None
                        detection_time_abs = None
                        detection_time_rel = None
                        print(f"No significant onset detected for event {evid}.")

                    self.saver.plot_onset_original_data(csv_times, csv_data, signal_start_time,
                                                        os.path.join(evid_dir, f'{evid}_ORIGINAL_ONSET.png'))

                    onset_time_predicted.append(signal_start_time)
                    onset_time_ground_truth.append(line_time)
                    audio_duration_list.append(audio_duration)
                    evid_list.append(evid)
                    filename_list.append(fname)
                    signal_start_time_list.append(signal_start_time)
                    detection_times_abs_list.append(detection_time_abs)
                    detection_times_rel_list.append(detection_time_rel)
                else:
                    print(f"Skipping row {index} due to insufficient data.")

            # Adding new keys to the result
            result = {
                'evid': evid_list,
                'filename': filename_list,
                'onset_time_ground_truth': onset_time_ground_truth,
                'audio_duration': audio_duration_list,
                'onset_time_predicted': onset_time_predicted,
                'detection_time_abs': detection_times_abs_list,  # Absolute time
                'detection_time_rel': detection_times_rel_list  # Relative time
            }
            df_result = pd.DataFrame(result)

            # Save the result DataFrame as a CSV file
            file_path = f'{self.save_result_dir}/results.csv'
            df_result.to_csv(file_path, index=False)
            return df_result
        else:
            raise ValueError('Unknown landscape')
