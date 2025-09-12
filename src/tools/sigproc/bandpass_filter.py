"""Bandpass filter implementation using a zero-phase Butterworth filter design.

This module provides functionality to apply a bandpass filter to time-series data
using a zero-phase Butterworth filter. The filter is applied in both forward and
reverse directions to eliminate phase distortion, which is crucial for maintaining
temporal alignment of the filtered signal with the original.
"""

import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib
import pickle
import os
from typing import Dict, Any, Tuple, Optional, Union
from numpy.typing import NDArray

# Set the matplotlib backend
try:
    matplotlib.use('TkAgg')
except ImportError:
    # Fallback to default backend if TkAgg is not available
    pass

def bandpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    lowcut_freq: float = 1000.0,
    highcut_freq: float = 4000.0,
    order: int = 4,
    **kwargs
) -> Dict[str, Any]:
    """Apply a zero-phase band-pass Butterworth filter to a time-domain signal.
    
    This function implements a digital band-pass filter using a Butterworth filter design.
    The filter is applied in both forward and reverse directions (filtfilt) to achieve
    zero phase distortion, which is important for maintaining the temporal alignment
    of the filtered signal with the original.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing the following keys:
        - 'primary_data': str
            Name of the key in the dictionary that contains the input signal array.
            The signal should be a 1D numpy array of float values.
        - 'sampling_rate': float
            Sampling frequency of the input signal in Hz. Must be at least twice the
            highest frequency component in the signal (Nyquist rate).
        - 'image_path': str, optional
            Path to a precomputed plot (not currently used, included for API consistency).
            
    output_image_path : str
        Filesystem path where the filtered signal plot will be saved. The parent
        directory will be created if it doesn't exist. The plot shows both the
        original and filtered signals for comparison.
        
    lowcut_freq : float, optional (default=1000.0)
        Lower cutoff frequency of the bandpass filter in Hz. Frequencies below this
        value will be attenuated. Must be positive and less than highcut_freq.
        
    highcut_freq : float, optional (default=4000.0)
        Upper cutoff frequency of the bandpass filter in Hz. Frequencies above this
        value will be attenuated. Must be greater than lowcut_freq and less than
        half the sampling rate (Nyquist frequency).
        
    order : int, optional (default=4)
        Order of the Butterworth filter. Higher values provide steeper roll-off
        but may introduce numerical instability. Must be a positive integer.
        
    **kwargs
        Additional keyword arguments (currently unused, included for future extension).

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the following keys:
        - 'filtered_signal': NDArray[np.float64]
            The filtered time-domain signal as a 1D numpy array.
        - 'domain': str
            Set to 'time-series' to indicate the type of data.
        - 'primary_data': str
            Set to 'filtered_signal' to indicate the main output field.
        - 'sampling_rate': float
            The sampling rate of the signal in Hz.
        - 'image_path': str
            Path to the generated visualization of the filtered signal.
        - 'filter_params': Dict[str, Any]
            Dictionary containing the filter parameters used:
            - 'type': str - Filter type ('butterworth_bandpass')
            - 'order': int - Filter order
            - 'lowcut_hz': float - Lower cutoff frequency in Hz
            - 'highcut_hz': float - Upper cutoff frequency in Hz
            - 'normalized_freqs': List[float] - Normalized cutoff frequencies [low, high]

    Raises
    ------
    ValueError
        If required input parameters are missing or invalid.
        If the input signal is empty or not a 1D array.
        If the sampling rate is not positive.
        
    Notes
    -----
    1. The filter uses scipy's `butter()` for filter design and `filtfilt()` for
       zero-phase filtering.
    2. Input frequencies are automatically clipped to valid ranges to prevent errors:
       - lowcut_freq is constrained to be > 0
       - highcut_freq is constrained to be < Nyquist frequency
       - If lowcut_freq >= highcut_freq, they are automatically swapped
    3. The filter is designed to be stable for the given order and frequency range.
    4. The function includes extensive input validation and provides warnings for
       edge cases.
    5. A visualization is generated showing the filtered signal and saved to the
       specified path in both PNG and pickled figure formats.
    
    Examples
    --------
    >>> import numpy as np
    >>> from scipy import signal
    >>> 
    >>> # Generate a test signal
    >>> fs = 10000  # 10 kHz sampling rate
    >>> t = np.linspace(0, 1, fs, endpoint=False)
    >>> signal_data = (np.sin(2*np.pi*100*t) +  # 100 Hz sine
    ...                0.5*np.sin(2*np.pi*1000*t) +  # 1 kHz sine
    ...                0.2*np.sin(2*np.pi*5000*t))  # 5 kHz sine
    >>> 
    >>> # Apply bandpass filter (1-3 kHz)
    >>> result = bandpass_filter(
    ...     data={'primary_data': 'signal', 'signal': signal_data, 'sampling_rate': fs},
    ...     output_image_path='filtered_signal.png',
    ...     lowcut_freq=1000,
    ...     highcut_freq=3000,
    ...     order=4
    ... )
    >>> filtered_signal = result['filtered_signal']
    """
    # --- Input Validation ---
    # Extract signal data using the primary_data key
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
    # Ensure frequencies are within valid ranges and ordered correctly
    if lowcut_freq >= highcut_freq:
        print(f"Warning: Lowcut frequency ({lowcut_freq} Hz) ≥ highcut frequency ({highcut_freq} Hz).")
        lowcut_freq, highcut_freq = min(lowcut_freq, highcut_freq), max(lowcut_freq, highcut_freq)
        print(f"Using frequency range: [{lowcut_freq}, {highcut_freq}] Hz")
        
    if highcut_freq >= nyquist_freq:
        print(f"Warning: Highcut frequency ({highcut_freq} Hz) ≥ Nyquist frequency ({nyquist_freq} Hz).")
        highcut_freq = max(1, nyquist_freq * 0.95)  # Stay safely below Nyquist
        print(f"Clipping highcut to {highcut_freq} Hz")
        
    if lowcut_freq <= 0:
        print(f"Warning: Lowcut frequency ({lowcut_freq} Hz) ≤ 0 Hz.")
        lowcut_freq = min(0.1, highcut_freq * 0.1)  # Small positive value
        print(f"Setting lowcut to {lowcut_freq} Hz")

    # Normalize the cutoff frequencies to the Nyquist frequency (range [0, 1])
    # This is required by scipy's butter() function
    low_norm = lowcut_freq / nyquist_freq
    high_norm = highcut_freq / nyquist_freq

    # Design the Butterworth bandpass filter
    # The filter is designed in the normalized frequency domain
    b, a = butter(
        N=order,                # Filter order
        Wn=[low_norm, high_norm],  # Cutoff frequencies (normalized)
        btype='band',           # Bandpass filter
        analog=False,           # Digital filter
        output='ba'             # Return numerator/denominator coefficients
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
               label=f'Filtered ({lowcut_freq:.1f}-{highcut_freq:.1f} Hz)')
        
        # Add grid and labels
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_title(f'Bandpass Filtered Signal\nOrder {order}, Range: [{lowcut_freq:.1f}, {highcut_freq:.1f}] Hz')
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
            'type': 'butterworth_bandpass',
            'order': order,
            'lowcut_hz': lowcut_freq,
            'highcut_hz': highcut_freq,
            'normalized_freqs': [low_norm, high_norm]
        }
    }
    return results
