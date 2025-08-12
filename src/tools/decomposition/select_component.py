import numpy as np
import matplotlib.pyplot as plt
import os, pickle

def select_component(
    data: dict,
    output_image_path: str,
    component_index: int
) -> dict:
    """
    Select one reconstructed component and emit it as a time-series signal.

    Parameters (in `data` dict expected keys):
    - new_params.signals_reconstructed: list[np.ndarray] reconstructed signals
    - sampling_rate: int

    Other parameters:
    - component_index: which component to select (0-based index)

    Returns:
    - dict with keys:
        signal_data, sampling_rate, domain ('time-series'), primary_data, image_path
    """
    signals_reconstructed = data['new_params'].get('signals_reconstructed')
    sampling_rate = data.get('sampling_rate')

    # --- Input Validation and Data Extraction ---  
    signal_data = signals_reconstructed[component_index]  # Assuming the index is valid and the list is not empty
    time_axis = np.arange(len(signal_data)) / sampling_rate

    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        ax.plot(time_axis, signal_data, color="#001A52", linewidth=0.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title('Selected Component Time Series')
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