import matplotlib.pyplot as plt
import os


class SaveImages:
    """
    Class for saving images of time-domain plots with additional event markers.
    """

    def create_dir(self, dir):
        """
        Create a directory if it doesn't already exist.

        Args:
            dir (str): Path to the directory to be created.
        """
        if not os.path.exists(dir):
            os.makedirs(dir)

    def save_image(self, csv_times, csv_data, line_time, output_image_path, color):
        """
        Save a time-domain plot of the signal with an event line.

        Args:
            csv_times (numpy.ndarray): Array of time values.
            csv_data (numpy.ndarray): Array of velocity (m/s) values.
            line_time (float): Time of the event onset.
            output_image_path (str): Path where the image will be saved.
            color (str): Color of the event line.

        Returns:
            None: Saves the image to the specified path.

        """
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(csv_times, csv_data, label='Velocity (m/s)')
        plt.axvline(x=line_time, color=color, linestyle='--', label='Event Time')  # Highlight the event time
        plt.title(f'Time Domain Plot')
        plt.xlabel('Time (sec)')
        plt.ylabel('Velocity (m/s)')
        plt.legend()

        # Save the plot as an image
        plt.savefig(output_image_path)
        plt.close()  # Close the figure to avoid display overlap

    def plot_onset_original_data(self, csv_times, csv_data, onset_time, output_image_path):
        """
        Save a time-domain plot of the original signal with an event onset marker.

        Args:
            csv_times (numpy.ndarray): Array of time values.
            csv_data (numpy.ndarray): Array of velocity (m/s) values.
            onset_time (float or None): Time of the event onset, if detected.
            output_image_path (str): Path where the image will be saved.

        Returns:
            None: Saves the image to the specified path.
        """
        # Create the plot
        plt.figure(figsize=(10, 6))

        # Plot the original time-domain signal
        plt.plot(csv_times, csv_data, label='Velocity (m/s)', color='blue')

        # Highlight the event onset time
        if onset_time is not None:
            plt.axvline(x=onset_time, color='red', linestyle='--', label='Event Time')

        # Add plot details
        plt.title('Time Domain Plot')
        plt.xlabel('Time (sec)')
        plt.ylabel('Velocity (m/s)')
        plt.legend(loc="upper right")

        # Save the plot as an image
        plt.savefig(output_image_path)
        plt.close()  # Close the figure to avoid display overlap
