import pandas as pd
from SpectralFluxMethod import SpectralFlux
from CalculateMetric import Metrics
import argparse
import os


def parse_args():
    # Set up argument parser to get command-line arguments
    parser = argparse.ArgumentParser(description="Inference script for seismic data.")

    # Argument for the path to the *.h5 input file
    parser.add_argument(
        '--input_file',
        type=str,
        required=True,
        help='Path to the input HDF5 file (*.h5)'
    )

    # Argument for the folder where the results will be saved
    parser.add_argument(
        '--output_folder',
        type=str,
        required=True,
        help='Folder to save the results'
    )

    # Optional argument to specify the landscape type (default is 'lunar')
    parser.add_argument(
        '--landscape',
        type=str,
        default='lunar',  # Default value is set to 'lunar'
        choices=['lunar', 'mars'],
        help='Specify landscape type.'
    )
    # Optional argument to specify the landscape type (default is 'lunar')
    # Optional argument to specify the mode (default is 'test')
    parser.add_argument(
        '--mode',
        type=str,
        default='test',  # Default value is set to 'test'
        choices=['train', 'test'],
        help='Specify whether you want to use this algorithm for prediction (train) or for testing against labeled data and measuring metrics (test).'
    )

    return parser.parse_args()


def main():
    # Get the arguments from the command line
    args = parse_args()

    # Check if the input file exists
    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} does not exist.")
        return

    # Check if the output folder exists, if not - create it
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
        print(f"Output folder {args.output_folder} created.")

    # Read data from the input HDF5 file
    data = pd.read_hdf(args.input_file)

    # Initialize and run spectral flux onset detection
    results = SpectralFlux(args.output_folder, data, args.landscape).onset_detection()

    # Process the file and save the results
    print(f"Processing file: {args.input_file}")

    # If spectral flux onset detection was successful, calculate metrics
    if results is not None and args.mode == 'train':
        calculate_metric = Metrics(results, args.output_folder)
        calculate_metric.calculate_metrics()
    # Select only the columns: 'filename', 'time_abs', and 'time_rel'
    detect_df = results[['filename', 'detection_time_abs', 'detection_time_rel']]

    # Rename columns to match the desired format
    detect_df = detect_df.rename(columns={
        'detection_time_abs': 'time_abs(%Y-%m-%dT%H:%M:%S.%f)',
        'detection_time_rel': 'time_rel(sec)'
    })

    # Save the filtered DataFrame to a CSV file
    detect_file_path = os.path.join(args.output_folder, "detections.csv")
    detect_df.to_csv(detect_file_path, index=False)

    print(f"Detections DataFrame saved to {detect_file_path}")
    # Print message indicating where the results are saved
    print(f"Saving results to folder: {args.output_folder}")


# Entry point for the script
if __name__ == "__main__":
    main()


