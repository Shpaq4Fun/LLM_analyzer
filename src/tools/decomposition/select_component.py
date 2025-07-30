import numpy as np
import matplotlib.pyplot as plt
import os

def select_component(
    data: dict,
    output_image_path: str,
    component_index: int
) -> dict:
    """
    Selects a specific component from a set of decomposed signals and outputs it as a time-series signal.

    Args:
        data (dict): The output dictionary from a previous tool. Must contain a list of reconstructed signals under a key like 'signals_reconstructed'.
        output_image_path (str): The full path where the output PNG image will be saved.
        component_index (int): The index of the component to select.

    Returns:
        dict: A dictionary containing the selected component as a time-series signal.
    """
    signals_reconstructed = data['new_params'].get('signals_reconstructed')
    sampling_rate = data.get('sampling_rate')

    # --- Input Validation and Data Extraction ---  
    signal_data = signals_reconstructed[component_index]  # Assuming the index is valid and the list is not empty
    time_axis = np.arange(len(signal_data)) / sampling_rate


    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    plt.plot(time_axis, signal_data, color="#001A52", linewidth=0.5)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title('Selected Component Time Series')
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