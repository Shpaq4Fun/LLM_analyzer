import numpy as np
from scipy.signal import hilbert
from scipy.fft import fft, fftfreq, fftshift
import matplotlib.pyplot as plt
import os
import pickle
from typing import Dict, Any, Tuple, Optional

def _compute_envelope_spectrum(
    signal: np.ndarray, 
    sampling_rate: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the envelope spectrum of a signal using the Hilbert transform and FFT.
    
    Parameters
    ----------
    signal : np.ndarray
        1D array containing the input time-domain signal
    sampling_rate : float
        Sampling frequency of the signal in Hz
        
    Returns
    -------
    tuple
        (frequencies, amplitudes) where:
        - frequencies: Array of frequency values in Hz
        - amplitudes: Array of amplitude values of the envelope spectrum
    
    Notes
    -----
    The envelope spectrum is computed by:
    1. Applying the Hilbert transform to get the analytic signal
    2. Taking the magnitude of the analytic signal to get the envelope
    3. Removing the DC component (mean) from the envelope
    4. Computing the one-sided FFT of the envelope
    """
    # Compute the analytic signal using Hilbert transform
    analytic_signal = hilbert(signal)
    
    # Get the envelope by taking the magnitude of the analytic signal
    envelope = np.abs(analytic_signal)
    
    # Remove DC component (mean) from the envelope
    envelope = envelope - np.mean(envelope)
    
    # Compute FFT of the envelope
    n = len(envelope)
    fft_vals = fft(envelope)
    
    # Get the one-sided spectrum
    n_onesided = n // 2
    amplitudes = 2.0/n * np.abs(fft_vals[:n_onesided])
    frequencies = fftfreq(n, 1.0/sampling_rate)[:n_onesided]
    
    return frequencies, amplitudes

def _compute_enhanced_envelope_spectrum(
    data_matrix: np.ndarray, 
    sampling_rate: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the enhanced envelope spectrum from a 2D data matrix (e.g., cyclic spectral coherence).
    
    This is done by summing the matrix along the first dimension (carrier frequency)
    to get an enhanced envelope spectrum, and then computing its spectrum via FFT.
    
    Parameters
    ----------
    data_matrix : np.ndarray
        2D array (e.g., cyclic spectral coherence map)
    sampling_rate : float
        Sampling frequency of the original signal in Hz
        
    Returns
    -------
    tuple
        (frequencies, amplitudes) where:
        - frequencies: Array of frequency values in Hz
        - amplitudes: Array of amplitude values of the enhanced envelope spectrum
    """
    # Sum the data matrix along the first dimension (carrier frequency axis)
    ees = np.sum(data_matrix, axis=0)
    
    # Remove DC component (mean) from the envelope
    ees = ees - np.mean(ees)
    
    # Compute FFT of the enhanced envelope
    n = len(ees)
    # fft_vals = fft(enhanced_envelope)
    
    # Get the one-sided spectrum
    n_onesided = n // 2
    # amplitudes = 2.0/n * np.abs(fft_vals[:n_onesided])
    frequencies = fftfreq(n, 1.0/sampling_rate)[:n_onesided]
    
    return frequencies, ees

def create_envelope_spectrum(
    data: Dict[str, Any],
    output_image_path: str,
    fft_normalization: str = 'amplitude',
    max_freq: Optional[float] = None,
    **plot_kwargs
) -> Dict[str, Any]:
    """
    Calculate and visualize the envelope spectrum of a time-domain signal.
    
    The envelope spectrum is useful for detecting periodic impacts or modulations
    in vibration signals, particularly in bearing and gearbox fault detection.
    
    Parameters
    ----------
    data : dict
        Dictionary containing the following keys:
        - 'primary_data': str, name of the array key holding the input time-domain signal (1D)
        - 'sampling_rate': float, sampling frequency in Hz
        - 'secondary_data': str, optional, for enhanced spectrum case
    output_image_path : str
        Path where the envelope spectrum plot will be saved
    fft_normalization : {'amplitude', 'power', 'psd'}, optional
        Type of FFT normalization to apply (default: 'amplitude')
    max_freq : float, optional
        Maximum frequency to display in the spectrum (Hz). If None, shows up to Nyquist.
    **plot_kwargs
        Additional keyword arguments passed to matplotlib's plot function
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'frequencies': np.ndarray, frequency values (Hz)
        - 'amplitudes': np.ndarray, amplitude values of the envelope spectrum
        - 'domain': str, set to 'frequency-spectrum'
        - 'primary_data': str, same as input
        - 'secondary_data': str, if provided in input
        - 'sampling_rate': float, sampling rate in Hz
        - 'image_path': str, path to the generated plot
        - 'metadata': dict, additional information about the processing
    
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
        raise ValueError("Empty signal data provided. Cannot compute envelope spectrum.")
        
    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        raise ValueError("No sampling rate provided. 'sampling_rate' is required in input dictionary.")
    
    N = len(signal_data)
    if N < 2:
        raise ValueError(f"Signal is too short ({N} samples). Need at least 2 samples.")
    
    # Ensure signal is 1D
   
    if signal_data.shape.__len__() == 1 or signal_data.shape.any() == 1:
        signal_data = signal_data.flatten()
        try:
            frequencies, amplitudes = _compute_envelope_spectrum(signal_data, float(sampling_rate))
            title = 'Envelope Spectrum'
        except Exception as e:
            raise RuntimeError(f"Failed to compute envelope spectrum: {str(e)}")
    elif signal_data.shape[0] > 1 and signal_data.shape[1] > 1:
        try:
            frequencies, amplitudes = _compute_enhanced_envelope_spectrum(signal_data, float(sampling_rate))
            title = 'Enhanced Envelope Spectrum'
        except Exception as e:
            raise RuntimeError(f"Failed to compute enhanced envelope spectrum: {str(e)}")
    else:
        raise ValueError("Input signal must be 1-dimensional. Got shape: {}".format(signal_data.shape))
    
    
    
    # --- Compute Envelope Spectrum ---
    
    
    # Apply frequency range limit if specified
    if max_freq is not None and max_freq > 0:
        mask = frequencies <= max_freq
        frequencies = frequencies[mask]
        amplitudes = amplitudes[mask]
    
    # --- Generate Visualization ---
    try:
        # Create figure with a larger size for better readability
        plt.figure(figsize=(12, 6))
        
        # Plot the envelope spectrum
        plt.plot(frequencies, amplitudes, 
                color=plot_kwargs.get('color', '#1f77b4'),
                linewidth=plot_kwargs.get('linewidth', 1.2),
                label=title)
        
        # Add grid and labels
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.title(title, fontsize=14, pad=15)
        plt.xlabel('Frequency [Hz]', fontsize=12)
        
        # Set y-label based on normalization type
        ylabel = {
            'amplitude': 'Amplitude',
            'power': 'Power/Frequency [dB/Hz]',
            'psd': 'Power Spectral Density [V²/Hz]'
        }.get(fft_normalization.lower(), 'Amplitude')
        plt.ylabel(ylabel, fontsize=12)
        
        # Set x-axis limits
        xlim = (0, 300)
        plt.xlim(xlim)
        
        # Add legend and adjust layout
        plt.legend(loc='upper right', framealpha=0.9)
        plt.tight_layout()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_image_path) or '.', exist_ok=True)
        
        # Save the figure
        plt.savefig(output_image_path, dpi=150, bbox_inches='tight')
        
        # Save figure object for potential later use
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")        
        with open(fig_path, 'wb') as f:
            pickle.dump(plt.gcf(), f)
            
        plt.close()
        
    except Exception as e:
        print(f"Warning: Could not generate envelope spectrum plot: {str(e)}")
        if not os.path.exists(output_image_path):
            # Create an empty plot if saving failed
            plt.figure()
            plt.text(0.5, 0.5, 'Plot generation failed', 
                    ha='center', va='center')
            plt.savefig(output_image_path)
            plt.close()
    
    # --- Prepare Results ---
    results = {
        'frequencies': frequencies,
        'amplitudes': amplitudes,
        'domain': 'frequency-spectrum',
        'primary_data': 'amplitudes',
        'secondary_data': 'frequencies',
        'sampling_rate': float(sampling_rate),
        'image_path': output_image_path,
        'metadata': {
            'fft_normalization': fft_normalization,
            'max_frequency_shown': float(max_freq if max_freq is not None else frequencies[-1]),
            'signal_length': N,
            'processing_steps': [
                'Hilbert transform to get analytic signal',
                'Envelope detection via magnitude',
                'DC component removal',
                'One-sided FFT of envelope'
            ]
        }
    }
    
    # Add secondary data if provided
    if 'secondary_data' in data:
        results['secondary_data'] = data['secondary_data']
    
    return results
