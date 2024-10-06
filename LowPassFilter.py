from scipy.signal import butter, filtfilt


class LPassFilter:
    """
    Class to apply a low-pass Butterworth filter to the input signal.
    """

    def filtering(self, data, cutoff, fs, order=4):
        """
        Apply a low-pass filter to the input data.

        Args:
            data (numpy.ndarray): The input signal data.
            cutoff (float): The cutoff frequency for the filter.
            fs (float): The sampling frequency of the input data.
            order (int): The order of the filter (default is 4).

        Returns:
            numpy.ndarray: The filtered signal.

        Raises:
            ValueError: If the cutoff frequency is invalid (e.g., less than or equal to zero).
        """
        nyquist = 0.5 * fs  # Calculate the Nyquist frequency
        low = cutoff / nyquist  # Normalize the cutoff frequency

        # Ensure the frequency range is within valid bounds
        low = min(low, 1.0)
        if low <= 0:
            raise ValueError("Invalid cutoff frequency for lowpass filter.")

        # Design a Butterworth low-pass filter
        b, a = butter(order, low, btype='low')

        # Apply the filter using filtfilt for zero-phase filtering
        y = filtfilt(b, a, data)

        return y
