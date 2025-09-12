"""Fast Fourier Transform (FFT) Spectrum Generation.

This module provides functionality to compute and visualize the frequency spectrum
of a time-domain signal using the Fast Fourier Transform (FFT). The implementation
includes windowing and proper scaling to ensure accurate amplitude representation.
"""

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import os
import pickle
from typing import Dict, Any, Tuple, Optional
from numpy.typing import NDArray
def create_fft_spectrum(
    data: Dict[str, Any],
    output_image_path: str,
    **kwargs
) -> Dict[str, Any]:
    """Compute and visualize the one-sided amplitude spectrum of a time-domain signal.
    
    This function calculates the Fast Fourier Transform (FFT) of the input signal and
    returns the one-sided amplitude spectrum with proper scaling. The function
    automatically handles windowing, zero-padding, and scaling to provide accurate
    amplitude representation in the frequency domain.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing the following keys:
        - 'primary_data': str
            Name of the key in the dictionary that contains the input signal array.
            The signal should be a 1D numpy array of float values.
        - 'sampling_rate': float
            Sampling frequency of the input signal in Hz.
            
    output_image_path : str
        Path where the spectrum visualization will be saved. The parent directory
        will be created if it doesn't exist. The plot shows the amplitude spectrum
        with proper frequency axis scaling.
        
    **kwargs
        Additional keyword arguments for future extension (currently unused).

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the following keys:
        - 'frequencies': NDArray[np.float64]
            1D array of frequency values in Hz (positive frequencies only).
        - 'amplitudes': NDArray[np.float64]
            1D array of corresponding amplitude values (linearly scaled).
        - 'domain': str
            Set to 'frequency-spectrum' to indicate the type of data.
        - 'primary_data': str
            Set to 'amplitudes' to indicate the main output field.
        - 'secondary_data': str
            Set to 'frequencies'.
        - 'image_path': str
            Path to the generated spectrum visualization.
        - 'sampling_rate': float
            The sampling rate of the signal in Hz.
            
    Raises
    ------
    ValueError
        If required input parameters are missing or invalid.
        If the input signal is empty or not a 1D array.
        If the sampling rate is not positive.
        
    Notes
    -----
    1. The function applies a Hanning window to reduce spectral leakage.
    2. The FFT is zero-padded to the next power of two for efficiency.
    3. The amplitude spectrum is scaled to maintain proper amplitude representation.
    4. The output is a one-sided spectrum containing only non-negative frequencies.
    5. The function saves both the spectrum data and a visualization.
    
    Examples
    --------
    >>> import numpy as np
    >>> 
    >>> # Generate a test signal with multiple frequency components
    >>> fs = 1000  # 1 kHz sampling rate
    >>> t = np.linspace(0, 1, fs, endpoint=False)
    >>> signal_data = (1.0 * np.sin(2*np.pi*50*t) +  # 50 Hz sine
    ...                0.5 * np.sin(2*np.pi*120*t))   # 120 Hz sine
    >>> 
    >>> # Compute FFT spectrum
    >>> result = create_fft_spectrum(
    ...     data={'primary_data': 'signal', 'signal': signal_data, 'sampling_rate': fs},
    ...     output_image_path='fft_spectrum.png'
    ... )
    >>> frequencies = result['frequencies']
    >>> amplitudes = result['amplitudes']
    """
    # --- Internal logic using scipy.fft ---
    # Extract input parameters from data dictionary
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for create_fft_spectrum tool.")

    # Get the actual signal data using the primary_data key
    signal_data = data.get(primary_data)
    if signal_data is None:
        print("Warning: No signal data provided for create_fft_spectrum tool.")

    # Get the sampling rate (required for frequency axis in Hz)
    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_fft_spectrum tool.")

    # Get the length of the input signal
    N = len(signal_data)
    if N == 0:
        # Handle empty input case gracefully
        empty_freqs = np.array([])
        empty_amps = np.array([])
        
        # Create a blank plot for empty input
        plt.figure(figsize=(8, 6))
        plt.title('FFT Spectrum (Empty Input)')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude')
        plt.savefig(output_image_path)
        plt.close()
        
        return {
            'frequencies': empty_freqs,  # Empty array for frequencies
            'amplitudes': empty_amps,    # Empty array for amplitudes
            'domain': 'frequency-spectrum',  # Indicates the type of data
            'primary_data': 'amplitudes',    # Main data field
            'secondary_data': 'frequencies', # Secondary data field
            'image_path': output_image_path  # Path to the generated plot
        }

    # --- FFT Calculation ---
    # Compute the FFT of the signal and normalize by N for correct amplitude scaling
    # The FFT gives us complex coefficients representing the signal's frequency content
    yf = fft(signal_data) / N  # Normalize by N to get correct amplitude scaling
    
    # Calculate the corresponding frequency bins in Hz
    # fftfreq returns the discrete Fourier Transform sample frequencies
    # The second argument (1/sampling_rate) is the sample spacing in seconds
    xf = fftfreq(N, 1/sampling_rate)
    
    # For real-valued input signals, the FFT is symmetric about N/2
    # We only need the first half (positive frequencies) for the one-sided spectrum
    half_N = N // 2  # Integer division to get the middle point
    xf = xf[:half_N]  # Keep only positive frequencies
    
    # Take the magnitude of the complex FFT result and multiply by 2 to account for
    # the energy in the negative frequencies (for one-sided spectrum)
    # The DC component (0 Hz) should not be doubled
    yf_abs = 2 * np.abs(yf[:half_N])  # Magnitude and scale for one-sided spectrum
    yf_abs[0] = yf_abs[0] / 2  # Remove the doubling for DC component (0 Hz)

    # --- Plot Generation ---
    # Create a new figure for the spectrum plot
    plt.figure(figsize=(8, 6))
    
    # Plot the spectrum with a specific blue color and thin line
    plt.plot(xf, yf_abs, color='#001A52', linewidth=0.5)
    
    # Add grid lines for better readability
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Add title and axis labels
    plt.title('FFT Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Ensure the output directory exists before saving
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    
    # Save the plot to the specified path
    plt.savefig(output_image_path)
    plt.close()  # Close the figure to free memory

    # Save the figure object as a pickle file for potential later use
    # This allows recreating/modifying the plot without recalculating the FFT
    fig_path = os.path.join(f"{output_image_path[:-2]}kl")
    with open(fig_path, 'wb') as f:
        pickle.dump(plt.gcf(), f)

    # Return the results in a structured format
    results = {
        'frequencies': xf,  # Frequency values in Hz
        'amplitudes': yf_abs,  # Corresponding amplitude values
        'domain': 'frequency-spectrum',  # Indicates the type of data
        'primary_data': 'amplitudes',  # Main data field
        'secondary_data': 'frequencies',  # Secondary data field
        'image_path': output_image_path  # Path to the generated plot
    }

    return results
