import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from typing import Dict, Any, List, Optional, Union
from numpy.typing import NDArray

class ComponentSelectionError(Exception):
    """Custom exception for component selection errors."""
    pass

def select_component(
    data: Dict[str, Any],
    output_image_path: str,
    component_index: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Select and extract a specific component from a set of reconstructed signals.
    
    This function is typically used after a signal decomposition (e.g., NMF, ICA) to select
    a specific component from the reconstructed signals and return it as a time-series signal.
    It also generates a visualization of the selected component.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing the following keys:
        - 'new_params': Dict[str, Any]
            Dictionary containing the 'signals_reconstructed' key which holds a list of
            numpy arrays representing the reconstructed signal components.
            Each array should be a 1D time series.
        - 'sampling_rate': float
            Sampling rate of the signal in Hz, used for time axis generation.
            
    output_image_path : str
        Path where the visualization of the selected component will be saved.
        The parent directory will be created if it doesn't exist.
        
    component_index : int
        Zero-based index of the component to select from the signals_reconstructed list.
        Must be a non-negative integer less than the number of available components.
        
    **kwargs
        Additional keyword arguments for future extensions.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the following keys:
        - 'signal_data': np.ndarray
            The selected component's time series data as a 1D numpy array.
        - 'sampling_rate': float
            The sampling rate of the signal in Hz.
        - 'domain': str
            Set to 'time-series' to indicate the type of data.
        - 'primary_data': str
            Set to 'signal_data' to indicate the main data field.
        - 'image_path': str
            Path to the saved visualization of the component.
        - 'component_index': int
            The index of the selected component.
            
    Raises
    ------
    KeyError
        If required keys are missing from the input data dictionary.
    IndexError
        If component_index is out of bounds for the available components.
    ComponentSelectionError
        If there's an issue with the component selection process.
        
    Notes
    -----
    - The function assumes that the input signals are already reconstructed and available
      in the 'new_params.signals_reconstructed' list.
    - The visualization includes the time series plot of the selected component with
      appropriate axis labels and grid for better readability.
    - The plot is saved as both an image file and a pickled figure object for potential
      later modification or analysis.
    """
    signals_reconstructed = data['new_params'].get('signals_reconstructed')
    sampling_rate = data.get('sampling_rate')

    # --- Input Validation and Data Extraction ---  
    signal_data = signals_reconstructed[component_index]  # Assuming the index is valid and the list is not empty
    time_axis = np.arange(len(signal_data)) / sampling_rate

    # --- Generate and save the visual output (always overwrite) ---
    fig, ax = plt.subplots(1,1,figsize=(7, 6))
    ax.plot(time_axis, signal_data, color="#001A52", linewidth=0.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_title(f'Selected Component Time Series (index={component_index})')
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
        'image_path': output_image_path,
        'component_index': int(component_index)
    }

    return results