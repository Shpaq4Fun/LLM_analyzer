import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib
import os
import pickle
from typing import Dict, Any

matplotlib.use('TkAgg')

def lowpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    cutoff_freq: float = 3500,
    order: int = 4
) -> Dict[str, Any]:
    """
    Apply a zero-phase low-pass Butterworth filter to a signal.
    
    This function implements a digital low-pass filter using a Butterworth filter design.
    The filter is applied in both forward and reverse directions (filtfilt) to achieve
    zero phase distortion, which is important for maintaining the temporal alignment
    of the filtered signal with the original.

    Parameters
    ----------
    data : dict
        Dictionary containing the following keys:
        - 'primary_data': str, name of the array key holding the input signal
        - 'sampling_rate': int, sampling frequency in Hz
    output_image_path : str
        Path where the filtered signal plot will be saved
    cutoff_freq : float, optional
        Cutoff frequency in Hz (default: 3500 Hz). Frequencies above this will be attenuated.
    order : int, optional
        Order of the Butterworth filter (default: 4). Higher order provides steeper
        roll-off but may introduce numerical instability.

    Returns
    -------
    dict
        A dictionary containing:
        - 'filtered_signal': np.ndarray, the filtered time-domain signal
        - 'domain': str, set to 'time-series' to indicate the type of data
        - 'primary_data': str, set to 'filtered_signal' for consistency
        - 'sampling_rate': float, the sampling rate of the signal in Hz
        - 'image_path': str, path to the generated plot
        - 'filter_params': dict, parameters used for filtering

    Notes
    -----
    - The filter uses scipy's butter() for filter design and filtfilt() for zero-phase filtering
    - The filter is designed to be stable for the given order and frequency range
    - Input frequencies are automatically validated and warnings are issued for edge cases
    - The function includes input validation and provides meaningful error messages
    """
    # --- Input Validation ---
    primary_data = data.get('primary_data')
    if primary_data is None:
        raise ValueError("No primary data key provided. Expected 'primary_data' in input dictionary.")

    signal_data = data.get(primary_data)
    if signal_data is None:
        raise ValueError(f"No signal data found for key '{primary_data}'. Cannot perform filtering.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        raise ValueError("No sampling rate provided. 'sampling_rate' is required in input dictionary.")

    # --- Filter Design ---
    # Nyquist frequency is half the sampling rate (maximum representable frequency)
    nyquist_freq = 0.5 * sampling_rate

    # --- Input Frequency Validation ---
    if cutoff_freq <= 0:
        raise ValueError(f"Cutoff frequency must be positive. Got {cutoff_freq} Hz")
        
    if cutoff_freq >= nyquist_freq:
        raise ValueError(
            f"Cutoff frequency ({cutoff_freq} Hz) must be below the Nyquist frequency "
            f"({nyquist_freq} Hz) to preserve signal content."
        )

    # Normalize the cutoff frequency to the Nyquist frequency (range [0, 1])
    # This is required by scipy's butter() function
    cutoff_norm = cutoff_freq / nyquist_freq
    normal_cutoff = cutoff_freq / nyquist_freq

    # Design the Butterworth lowpass filter
    # The filter is designed in the normalized frequency domain
    b, a = butter(
        N=order,              # Filter order
        Wn=cutoff_norm,       # Normalized cutoff frequency (0-1)
        btype='low',          # Lowpass filter
        analog=False,         # Digital filter
        output='ba'           # Return numerator/denominator coefficients
    )

    # --- Apply the Filter ---
    # filtfilt applies the filter twice (forward and backward) to achieve zero phase
    # This ensures the filtered signal is not time-shifted relative to the original
    filtered_signal = filtfilt(
        b,                  # Numerator coefficients
        a,                  # Denominator coefficients
        signal_data,        # Input signal
        padlen=3*(max(len(a), len(b)) - 1)  # Padding for transients
    )

    # --- Generate Visualization ---
    time_axis = np.arange(len(signal_data)) / sampling_rate
    
    if not os.path.isfile(output_image_path):
        # Create a new figure with specified dimensions
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        
        # Plot the filtered signal
        ax.plot(time_axis, filtered_signal, color="#001A52", linewidth=0.7, 
               label=f'Filtered (<{cutoff_freq:.1f} Hz)')
        
        # Add grid and labels
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_title(f'Lowpass Filtered Signal\nOrder {order}, Cutoff: {cutoff_freq:.1f} Hz')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.legend(loc='upper right')
        ax.set_xlim(0, time_axis[-1])
        
        # Adjust layout and save the figure
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_image_path) or '.', exist_ok=True)
        plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
        
        # Save the figure object for potential later use
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close(fig)

    # --- Prepare Results ---
    results = {
        'filtered_signal': filtered_signal,  # The filtered time-domain signal
        'domain': 'time-series',             # Indicates the type of data
        'primary_data': 'filtered_signal',   # Main data field for downstream processing
        'sampling_rate': float(sampling_rate), # Ensure numeric type
        'image_path': output_image_path,     # Path to the generated plot
        'filter_params': {                   # Store filter parameters for reference
            'type': 'butterworth_lowpass',
            'order': order,
            'cutoff_hz': cutoff_freq,
            'normalized_cutoff': cutoff_norm
        }
    }
    return results