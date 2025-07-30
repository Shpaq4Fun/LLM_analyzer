import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('TkAgg')


def load_data(
    signal_data: np.ndarray,
    sampling_rate: int,
    output_image_path: str
) -> dict:
    """
    Simulates loading data and generates a time-series plot.
    In a real scenario, this tool would handle actual data loading from a file path.
    For this pipeline, it visualizes the already loaded signal.

    Args:
        signal_data (np.ndarray): 1D NumPy array containing the time-series signal.
        sampling_rate (int): The sampling frequency of the signal in Hz.
        output_image_path (str): The full path where the output PNG image will be saved.

    Returns:
        dict: A dictionary containing the results, with the following keys:
              'signal_data' (np.ndarray): The input signal data.
              'sampling_rate' (int): The input sampling rate.
              'image_path' (str): The path where the output image was saved.
    """
    # print('=============================================================================')
    print(sampling_rate)
    if signal_data is None or len(signal_data) == 0:
        print("Warning: No signal data provided for load_data tool.")
        # Create a blank plot
        plt.figure(figsize=(10, 8))
        plt.title('Time Series Data (No Data)')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.savefig(output_image_path)
        plt.close()
        return {
            'signal_data': np.array([]),
            'sampling_rate': sampling_rate,
            'domain': 'time-series',
            'image_path': output_image_path
        }
    signal_data = signal_data[:min(len(signal_data), round(1*sampling_rate))]
    time_axis = np.arange(len(signal_data)) / sampling_rate

    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    plt.plot(time_axis, signal_data, color="#001A52", linewidth=0.5)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title('Loaded Time Series Data')
    plt.axis('tight')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()

    # --- Return the structured data output ---
    results = {
        'signal_data': signal_data,
        'sampling_rate': sampling_rate,
        'domain': 'time-series',
        'primary_data': 'signal_data',
        'image_path': output_image_path
    }

    return results