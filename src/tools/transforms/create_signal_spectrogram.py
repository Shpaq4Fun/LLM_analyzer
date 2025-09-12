import numpy as np
import scipy.signal
import os
import matplotlib.pyplot as plt
import pickle
import json
from typing import Dict, Any, Tuple, Optional, Union
import warnings

def _compute_spectrogram(
    signal: np.ndarray,
    sampling_rate: float,
    nperseg: int = 128,
    noverlap: Optional[int] = 110,
    nfft: Optional[int] = 256
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute a spectrogram using the Short-Time Fourier Transform (STFT).
    
    This is a wrapper around scipy.signal.spectrogram with additional
    parameter validation and error handling.
    
    Parameters
    ----------
    signal : np.ndarray
        1D array containing the input time-domain signal
    sampling_rate : float
        Sampling frequency of the signal in Hz
    window : str or tuple or array_like, optional
        Desired window to use. Default is 'hann'.
    nperseg : int, optional
        Length of each segment. Default is 128.
    noverlap : int, optional
        Number of points to overlap between segments. If None, noverlap = nperseg // 2.
    nfft : int, optional
        Length of the FFT used. If None, uses power of 2 >= nperseg.
        
    Returns
    -------
    f : ndarray
        Array of sample frequencies.
    t : ndarray
        Array of segment times.
    Sxx : ndarray
        Spectrogram of x. By default, the last axis of Sxx corresponds to the 
        segment times.
    
    Raises
    ------
    ValueError
        If input parameters are invalid
    """
    # Validate input parameters
    if signal.size == 0:
        raise ValueError("Input signal is empty.")
    
    if sampling_rate <= 0:
        raise ValueError("Sampling rate must be positive.")
    
    if nperseg <= 0:
        raise ValueError("Window length (nperseg) must be positive.")
    
    if noverlap >= nperseg:
        warnings.warn(
            f"noverlap={noverlap} is greater than or equal to nperseg={nperseg}. "
            f"Using noverlap = nperseg // 2 = {nperseg // 2}"
        )
        noverlap = nperseg // 2
    
    # Compute the spectrogram
    f, t, Sxx = scipy.signal.spectrogram(
        signal,
        fs=sampling_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft
    )
    
    return f, t, Sxx

def create_signal_spectrogram(
    data: Dict[str, Any],
    output_image_path: str,
    nperseg: int = 128,
    noverlap: Optional[int] = 110,
    nfft: Optional[int] = 256,
    cmap: str = 'jet',
    **plot_kwargs
) -> Dict[str, Any]:
    """
    Calculate and visualize a spectrogram for a time-series signal.
    
    This function computes a time-frequency representation of a signal using the
    Short-Time Fourier Transform (STFT) and generates a visualization of the
    spectrogram.
    
    Parameters
    ----------
    data : dict
        Dictionary containing the following keys:
        - 'primary_data': str, name of the array key holding the input signal (1D)
        - 'sampling_rate': float, sampling frequency in Hz
    output_image_path : str
        Path where the spectrogram plot will be saved
    nperseg : int, optional
        Length of each segment. Default is 128.
    noverlap : int, optional
        Number of points to overlap between segments. If None, noverlap = nperseg // 2.
    nfft : int, optional
        Length of the FFT used. If None, uses power of 2 >= nperseg.
    cmap : str, optional
        Colormap to use for the spectrogram. Default is 'jet'.
    **plot_kwargs
        Additional keyword arguments passed to matplotlib's pcolormesh function.
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'frequencies': np.ndarray, frequency values (Hz)
        - 'times': np.ndarray, time values (s)
        - 'Sxx': np.ndarray, spectrogram matrix (time-frequency representation)
        - 'domain': str, set to 'time-frequency-matrix'
        - 'primary_data': str, set to 'Sxx' for consistency
        - 'secondary_data': str, set to 'frequencies'
        - 'tertiary_data': str, set to 'times'
        - 'sampling_rate': float, sampling rate in Hz
        - 'nperseg': int, length of each segment used
        - 'noverlap': int, overlap between segments
        - 'image_path': str, path to the generated plot
    
    Raises
    ------
    ValueError
        If required input data is missing or invalid
    """
    # --- Input Validation ---
    primary_data = data.get('primary_data')
    if primary_data is None:
        raise ValueError("No primary data key provided. Expected 'primary_data' in input dictionary.")

    signal_data = np.asarray(data.get(primary_data))
    if signal_data.size == 0:
        raise ValueError("Empty signal data provided. Cannot compute spectrogram.")
        
    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        raise ValueError("No sampling rate provided. 'sampling_rate' is required in input dictionary.")
    
    # Convert parameters to appropriate types if needed
    try:
        if isinstance(nperseg, str):
            nperseg = int(nperseg)
        if isinstance(noverlap, str):
            noverlap = int(noverlap)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid window parameters: {str(e)}")
    
    # Ensure signal is 1D
    if signal_data.ndim > 1:
        if signal_data.shape[0] == 1 or signal_data.shape[1] == 1:
            signal_data = signal_data.flatten()
        else:
            raise ValueError("Input signal must be 1-dimensional. Got shape: {}".format(signal_data.shape))
    
    # --- Compute Spectrogram ---
    try:
        f, t, Sxx = _compute_spectrogram(
            signal=signal_data,
            sampling_rate=float(sampling_rate),
            nperseg=nperseg,
            noverlap=noverlap,
            nfft=nfft
        )
        # print(f[0], f[-1], t[0], t[-1])
    except Exception as e:
        raise RuntimeError(f"Failed to compute spectrogram: {str(e)}")
    
    # Convert to dB for visualization if in PSD mode
    Sxx_db = 10 * np.log10(Sxx + np.finfo(float).eps)  # Add epsilon to avoid log(0)
    zlabel = 'Power/Frequency (dB/Hz)'

    # --- Generate Visualization ---
    try:
        # Create figure with specified size
        plt.figure(figsize=(12, 6))
        
        # Create the spectrogram plot
        plt.pcolormesh(
            t, f, Sxx_db,
            shading='gouraud',
            cmap=cmap,
            **plot_kwargs
        )
        
        # Add colorbar
        cbar = plt.colorbar()
        cbar.set_label(zlabel, rotation=270, labelpad=15)
        
        # Add labels and title
        plt.title('Spectrogram', fontsize=14, pad=15)
        plt.xlabel('Time [s]', fontsize=12)
        plt.ylabel('Frequency [Hz]', fontsize=12)
        
        # Set y-axis to log scale for better frequency resolution
        # plt.yscale('log')
        
        # Adjust layout
        plt.tight_layout()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_image_path) or '.', exist_ok=True)
        
        # Save the figure
        plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
        
        # Save figure object for potential later use
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as file_handle:
            pickle.dump(plt.gcf(), file_handle)
            
        plt.close()
        
    except Exception as e:
        print(f"Warning: Could not generate spectrogram plot: {str(e)}")
        if not os.path.exists(output_image_path):
            # Create an empty plot if saving failed
            plt.figure()
            plt.text(0.5, 0.5, 'Spectrogram plot generation failed', 
                    ha='center', va='center')
            plt.savefig(output_image_path)
            plt.close()
    
    # --- Prepare Results ---
    results = {
        'frequencies': f,
        'times': t,
        'Sxx': Sxx,
        'domain': 'time-frequency-matrix',
        'primary_data': 'Sxx',
        'secondary_data': 'frequencies',
        'tertiary_data': 'times',
        'sampling_rate': sampling_rate,
        'nperseg': nperseg,
        'noverlap': noverlap,
        'nfft': nfft,
        'image_path': output_image_path
    }
    
    return results
