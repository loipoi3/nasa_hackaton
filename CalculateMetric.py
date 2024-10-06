import pandas as pd
import os

class Metrics:
    """
    Class to calculate and save performance metrics for seismic data onset predictions.
    """
    def __init__(self, results, saved_dir):
        """
        Initialize the Metrics class.

        Args:
            results (pandas.DataFrame): DataFrame containing onset predictions, ground truth, and audio durations.
            saved_dir (str): Directory where the metrics will be saved as a CSV file.
        """
        self.results = results
        self.saved_dir = saved_dir

    def _calculate_median_send_signal_percentage_predicted(self):
        """
        Calculate the median send signal percentage based on predicted onset times.

        Args:
            None

        Returns:
            float: The median send signal percentage for predicted onset times.
        """
        self.results['median_send_signal_persantage_predicted'] = 100 - (
                    (self.results['onset_time_predicted'] / self.results['audio_duration']) * 100)
        return self.results['median_send_signal_persantage_predicted'].median()

    def _calculate_median_send_signal_percentage_truth(self):
        """
        Calculate the median send signal percentage based on ground truth onset times.

        Args:
            None

        Returns:
            float: The median send signal percentage for ground truth onset times.
        """
        self.results['mean_send_signal_persantage_truth'] = 100 - (
                (self.results['onset_time_ground_truth'] / self.results['audio_duration']) * 100)
        return self.results['mean_send_signal_persantage_truth'].median()

    def _calculate_median_percentage_difference(self, median_predicted, median_truth):
        """
        Calculate the difference between the median percentages of predicted and ground truth onset times.

        Args:
            median_predicted (float): Median send signal percentage for predicted onset times.
            median_truth (float): Median send signal percentage for ground truth onset times.

        Returns:
            float: The difference between the truth and predicted median send signal percentages.
        """
        return median_truth - median_predicted

    def _calculate_median_time_deviation_predicted(self):
        """
        Calculate the median time deviation between predicted and ground truth onset times.

        Args:
            None

        Returns:
            float: The median time deviation between predicted and ground truth onset times.
        """
        self.results['onset_time_deviation'] = abs(self.results['onset_time_ground_truth'] - self.results['onset_time_predicted'])
        median_deviation = self.results['onset_time_deviation'].median()
        return median_deviation

    def _calculate_median_signal_reduction(self, median_predicted):
        """
        Calculate the median reduction of send signal based on predicted onset times.

        Args:
            median_predicted (float): Median send signal percentage for predicted onset times.

        Returns:
            float: The median reduction in send signal for predicted onset times.
        """
        return 100 - median_predicted

    def calculate_metrics(self):
        """
        Calculate all relevant metrics including:
            - Median time deviation.
            - Median send signal percentages for predicted and ground truth values.
            - Median percentage difference.
            - Median reduction of send signal.

        The metrics are saved as a CSV file in the specified directory.

        Args:
            None

        Returns:
            pandas.DataFrame: A DataFrame containing the calculated metrics.
        """
        # Calculate median deviation
        median_deviation = self._calculate_median_time_deviation_predicted()

        # Calculate median send signal percentages for both predicted and ground truth
        median_predicted = self._calculate_median_send_signal_percentage_predicted()
        median_truth = self._calculate_median_send_signal_percentage_truth()

        # Calculate the difference between predicted and ground truth median percentages
        median_difference = self._calculate_median_percentage_difference(median_predicted, median_truth)

        # Calculate the median reduction in send signal for predicted onset times
        median_signal_reduction = self._calculate_median_signal_reduction(median_predicted)

        # Prepare metrics dictionary
        metrics = {
            'median_send_signal_percentage_predicted': median_predicted,
            'median_send_signal_percentage_truth': median_truth,
            'median_percentage_difference': median_difference,
            'median_time_deviation': median_deviation,
            'median_signal_reduction': median_signal_reduction
        }

        # Output to console for verification
        print(f"Median deviation: {median_deviation} sec.")
        print(f"Median send signal percentage (Predicted): {median_predicted} %")
        print(f"Median send signal percentage (Truth): {median_truth} %")
        print(f"Median percentage difference: {median_difference} %")
        print(f"Median signal reduction: {median_signal_reduction} %")

        # Saving the metrics to a CSV file
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(os.path.join(self.saved_dir, 'mars_metrics.csv'), index=False)
        return metrics_df
