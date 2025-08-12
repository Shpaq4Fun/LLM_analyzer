import numpy as np
import matplotlib.pyplot as plt
import os, pickle
import matplotlib
matplotlib.use('TkAgg')


def load_data(
    signal_data: np.ndarray,
    sampling_rate: int,
    output_image_path: str
) -> dict:
    """
    Visualize (and lightly trim) an already loaded time-series signal.

    This tool does not read from disk; it simply plots the provided arrays
    and wraps them in a standard dictionary used by subsequent tools.

    Parameters:
    - signal_data: 1D NumPy array
    - sampling_rate: Hz
    - output_image_path: where to save the PNG of the plot

    Returns:
    - dict with keys: signal_data, sampling_rate, domain ('time-series'), image_path,
      primary_data
    """
    # print('=============================================================================')
    print(sampling_rate)
    if signal_data is None or len(signal_data) == 0:
        print("Warning: No signal data provided for load_data tool.")
        # Create a blank plot
        plt.figure(figsize=(7, 6))
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
    signal_data = signal_data[:min(len(signal_data), round(2*sampling_rate))]
    time_axis = np.arange(len(signal_data)) / sampling_rate

    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        ax.plot(time_axis, signal_data, color="#001A52", linewidth=0.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title('Loaded Time Series Data')
        ax.axis('tight')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        plt.tight_layout()
        plt.savefig(output_image_path)
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
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