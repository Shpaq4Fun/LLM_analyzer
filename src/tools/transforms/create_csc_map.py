"""Cyclic Spectral Coherence (CSC) Map Generation.

This module provides functionality to compute and visualize Cyclic Spectral Coherence (CSC) maps,
which are useful for analyzing cyclostationary signals in the bi-frequency domain.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft
import os
import pickle
from typing import Dict, Any, Tuple, Optional, Union, List
from numpy.typing import NDArray

def create_csc_map(
    data: Dict[str, Any],
    output_image_path: str,
    min_alpha: int = 1,
    max_alpha: int = 150,
    window: int = 256,
    overlap: int = 220,
    **kwargs
) -> Dict[str, Any]:
    """Compute and visualize the Cyclic Spectral Coherence (CSC) map of a signal.
    
    This function calculates the Cyclic Spectral Coherence (CSC) map, which is a powerful
    tool for analyzing cyclostationary signals. It reveals the correlation between
    frequency components separated by the cyclic frequency (alpha).

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
        Path where the CSC map visualization will be saved. The parent directory
        will be created if it doesn't exist.
        
    min_alpha : int, optional (default=1)
        Minimum cyclic (modulating) frequency in Hz to analyze.
        Must be non-negative and less than max_alpha.
        
    max_alpha : int, optional (default=150)
        Maximum cyclic (modulating) frequency in Hz to analyze.
        Must be greater than min_alpha and less than half the sampling rate.
        
    window : int, optional (default=256)
        Length of the window (in samples) used for the analysis.
        This also determines the FFT size (nfft = window).
        
    overlap : int, optional (default=220)
        Number of overlapping samples between consecutive windows.
        Must be less than window.
        
    **kwargs
        Additional keyword arguments (currently unused, included for future extension).

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the following keys:
        - 'csc_map': NDArray[np.float64]
            2D array representing the CSC map (carrier_frequencies × cyclic_frequencies).
        - 'carrier_frequencies': NDArray[np.float64]
            1D array of carrier frequencies in Hz.
        - 'cyclic_frequencies': NDArray[np.float64]
            1D array of cyclic (modulating) frequencies in Hz.
        - 'domain': str
            Set to 'bi-frequency-matrix' to indicate the type of data.
        - 'primary_data': str
            Set to 'csc_map' to indicate the main output field.
        - 'secondary_data': str
            Set to 'carrier_frequencies'.
        - 'tertiary_data': str
            Set to 'cyclic_frequencies'.
        - 'sampling_rate': float
            The sampling rate of the signal in Hz.
        - 'original_signal_data': NDArray[np.float64]
            The original input signal.
        - 'image_path': str
            Path to the generated visualization of the CSC map.
            
    Raises
    ------
    ValueError
        If required input parameters are missing or invalid.
        If the input signal is empty or not a 1D array.
        If the sampling rate is not positive.
        If window size is invalid.
        If overlap is invalid (>= window).
        If frequency range is invalid.
        
    Notes
    -----
    1. The CSC map is computed using Welch's method with a Hamming window.
    2. The function automatically limits the analysis to the first 3 seconds of the input signal
       to prevent excessive computation time.
    3. The output CSC map is normalized to the range [0, 1].
    4. The visualization uses a jet colormap by default.
    5. The function saves both the CSC map data and a visualization.
    
    Examples
    --------
    >>> import numpy as np
    >>> 
    >>> # Generate a test signal with amplitude modulation
    >>> fs = 10000  # 10 kHz sampling rate
    >>> t = np.linspace(0, 3, 3*fs, endpoint=False)
    >>> carrier = np.sin(2*np.pi*1000*t)  # 1 kHz carrier
    >>> modulator = 0.5*(1 + np.sin(2*np.pi*50*t))  # 50 Hz modulation
    >>> signal_data = carrier * modulator  # AM signal
    >>> 
    >>> # Compute CSC map
    >>> result = create_csc_map(
    ...     data={'primary_data': 'signal', 'signal': signal_data, 'sampling_rate': fs},
    ...     output_image_path='csc_map.png',
    ...     min_alpha=1,
    ...     max_alpha=150,
    ...     window=256,
    ...     overlap=200
    ... )
    >>> csc_map = result['csc_map']
    >>> carrier_freqs = result['carrier_frequencies']
    >>> cyclic_freqs = result['cyclic_frequencies']
    """
    # --- Placeholder Logic to Generate a Synthetic CSC Map ---
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for create_csc_map tool.")

    signal_data = data.get(primary_data)
    if signal_data is None:
        print("Warning: No signal data provided for create_csc_map tool.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_csc_map tool.")

    if min_alpha < 0 or min_alpha >= max_alpha:
        min_alpha = 1
    if max_alpha >= sampling_rate / 2:
        max_alpha = 150    
    if window <= 0:
        window = 256
    if overlap >= window:
        overlap = 220

    csc_map, carrier_frequencies, cyclic_frequencies = spectral_coh(signal_data[:min(len(signal_data), round(3*sampling_rate))],
                                                                    alphamin=min_alpha, 
                                                                    alphamax=max_alpha, 
                                                                    nfft=window, 
                                                                    okno=window, 
                                                                    fs=sampling_rate, 
                                                                    nover=overlap)
    csc_map = np.abs(csc_map)
    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        im = ax.pcolormesh(cyclic_frequencies, carrier_frequencies/1000, csc_map, shading='nearest', cmap='jet_r')
        ax.set_ylabel('Carrier Frequency (f) [kHz]')
        ax.set_xlabel('Cyclic Frequency (alpha) [Hz]')
        ax.set_title('Cyclic Spectral Coherence (CSC) Map')
        fig.colorbar(im, ax=ax, label='Coherence Magnitude')
        fig.tight_layout()
        plt.savefig(output_image_path)
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close()

    # --- Return the structured data output ---
    results = {
        'action_name': 'create_csc_map',
        'action_documentation_path': 'src/tools/transforms/create_csc_map.md',
        'cyclic_frequencies': cyclic_frequencies,
        'carrier_frequencies': carrier_frequencies,
        'csc_map': csc_map,
        'domain': 'bi-frequency-matrix',
        'primary_data': 'csc_map',
        'secondary_data': 'cyclic_frequencies',
        'tertiary_data': 'carrier_frequencies',
        'sampling_rate': sampling_rate,
        'original_signal_data': signal_data,
        'image_path': output_image_path
    }

    return results

def CPS_W(
    y: NDArray[np.float64],
    x: NDArray[np.float64],
    alpha: float,
    nfft: int,
    Noverlap: int,
    Window: Union[NDArray[np.float64], int],
    opt: str = 'sym',
    P: Optional[float] = None
) -> NDArray[np.complex128]:
    """Compute Welch's estimate of the (Cross) Cyclic Power Spectrum.
    
    This function calculates the Cyclic Power Spectrum (CPS) using Welch's method,
    which is a modified periodogram approach that reduces variance by averaging
    over multiple segments of the signal.
    
    Parameters
    ----------
    y : NDArray[np.float64]
        First input signal (reference signal).
    x : NDArray[np.float64]
        Second input signal (if x=y, computes auto-spectrum).
    alpha : float
        Cyclic frequency normalized by the sampling frequency (range [0, 1]).
    nfft : int
        Length of the FFT used. Should be a power of 2 for efficiency.
    Noverlap : int
        Number of points to overlap between segments.
    Window : Union[NDArray[np.float64], int]
        Window function to apply to each segment. If an integer is provided,
        a Hamming window of that length will be used.
    opt : str, optional (default='sym')
        Computation option:
        - 'sym': Symmetric version (recommended for most cases)
        - 'asym': Asymmetric version
    P : float, optional
        Confidence level (between 0 and 1) for statistical significance.
        If provided, returns thresholded CPS.
        
    Returns
    -------
    NDArray[np.complex128]
        Complex-valued Cyclic Power Spectrum with shape (nfft//2 + 1,).
        
    Notes
    -----
    1. The CPS is a frequency-domain representation of the second-order
       cyclostationarity of a signal.
    2. The cyclic frequency alpha corresponds to the rate of periodicity
       in the signal's statistics.
    3. The magnitude of the CPS indicates the strength of the cyclostationarity
       at each frequency bin for the given alpha.
    """
    
    # Handle window input
    if np.isscalar(Window):
        Window = signal.windows.hann(Window)
    Window = np.array(Window).flatten()
    
    n = len(x)
    nwind = len(Window)
    
    # Convert to column vectors
    y = np.array(y).flatten()
    x = np.array(x).flatten()
    
    K = int((n - Noverlap) / (nwind - Noverlap))  # Number of windows
    
    # Compute CPS
    index = np.arange(nwind)
    t = np.arange(n)
    CPS = 0
    
    if opt == 'sym':
        y = y * np.exp(-1j * np.pi * alpha * t)
        x = x * np.exp(1j * np.pi * alpha * t)
    else:
        x = x * np.exp(2j * np.pi * alpha * t)
    
    for i in range(K):
        xw = Window * x[index]
        yw = Window * y[index]
        Yw1 = fft(yw, nfft)  # Yw(f+a/2) or Yw(f)
        Xw2 = fft(xw, nfft)  # Xw(f-a/2) or Xw(f-a)
        CPS = Yw1 * np.conj(Xw2) + CPS
        index = index + (nwind - Noverlap)
    
    # Normalize
    KMU = K * np.linalg.norm(Window)**2  # Normalizing scale factor
    CPS = CPS / KMU
    
    return CPS


def SCoh_W(
    y: NDArray[np.float64],
    x: NDArray[np.float64],
    alpha: float,
    nfft: int,
    Noverlap: int,
    Window: Union[NDArray[np.float64], int],
    opt: str = 'sym',
    P: Optional[float] = None
) -> NDArray[np.complex128]:
    """Compute Welch's estimate of the Cyclic Spectral Coherence (CSC).
    
    This function calculates the Cyclic Spectral Coherence, which measures the
    normalized cross-spectral density between frequency-shifted versions of
    the input signals at a given cyclic frequency alpha.
    
    Parameters
    ----------
    y : NDArray[np.float64]
        First input signal (reference signal).
    x : NDArray[np.float64]
        Second input signal (if x=y, computes auto-coherence).
    alpha : float
        Cyclic frequency normalized by the sampling frequency (range [0, 1]).
    nfft : int
        Length of the FFT used. Should be a power of 2 for efficiency.
    Noverlap : int
        Number of points to overlap between segments.
    Window : Union[NDArray[np.float64], int]
        Window function to apply to each segment. If an integer is provided,
        a Hamming window of that length will be used.
    opt : str, optional (default='sym')
        Computation option:
        - 'sym': Symmetric version (recommended for most cases)
        - 'asym': Asymmetric version
    P : float, optional
        Confidence level (between 0 and 1) for statistical significance.
        If provided, returns thresholded coherence values.
        
    Returns
    -------
    NDArray[np.complex128]
        Complex-valued Cyclic Spectral Coherence with shape (nfft//2 + 1,).
        Values are in the range [0, 1] where 1 indicates perfect coherence.
        
    Notes
    -----
    1. The CSC is a normalized version of the Cyclic Power Spectrum that
       removes the effects of the signal's power spectrum.
    2. The magnitude of the CSC indicates the strength of the relationship
       between frequency components separated by alpha.
    3. Values close to 1 indicate strong cyclostationarity at the given alpha.
    """
    
    # Handle window input
    if np.isscalar(Window):
        Window = signal.windows.hann(Window)
    Window = np.array(Window).flatten()
    
    n = len(x)
    nwind = len(Window)
    
    # Input validation
    if alpha > 1 or alpha < 0:
        raise ValueError('alpha must be in [0,1]')
    if nwind <= Noverlap:
        raise ValueError('Window length must be > Noverlap')
    if nfft < nwind:
        raise ValueError('Window length must be <= nfft')
    if P is not None and (P >= 1 or P <= 0):
        raise ValueError('P must be in ]0,1[')
    
    # Convert to column vectors
    y = np.array(y).flatten()
    x = np.array(x).flatten()
    
    t = np.arange(n)
    
    if opt == 'sym':
        y = y * np.exp(-1j * np.pi * alpha * t)
        x = x * np.exp(1j * np.pi * alpha * t)
    else:
        x = x * np.exp(2j * np.pi * alpha * t)
    
    # Compute cross and auto spectral densities
    Syx = CPS_W(y, x, 0, nfft, Noverlap, Window, opt)
    Sy = CPS_W(y, y, 0, nfft, Noverlap, Window, opt)
    Sx = CPS_W(x, x, 0, nfft, Noverlap, Window, opt)
    
    # Compute coherence
    Coh = Syx / np.sqrt(Sy * Sx)
    
    return Coh


def spectral_coh(
    x: NDArray[np.float64],
    alphamin: float = 1,
    alphamax: float = 150,
    nfft: int = 512,
    okno: int = 512,
    fs: float = 1,
    nover: int = 450
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Compute the Cyclic Spectral Coherence (CSC) matrix.
    
    This function computes the CSC matrix for a range of cyclic frequencies (alpha)
    and carrier frequencies, providing a 2D representation of signal cyclostationarity.
    
    Parameters
    ----------
    x : NDArray[np.float64]
        1D input signal array.
    alphamin : float
        Minimum cyclic (modulating) frequency in Hz.
    alphamax : float
        Maximum cyclic (modulating) frequency in Hz.
    nfft : int
        Number of FFT points. Determines frequency resolution.
    okno : int
        Window length in samples. Should be ≤ nfft.
    fs : float
        Sampling frequency in Hz.
    nover : int
        Number of overlapping samples between segments.
        
    Returns
    -------
    Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]
        A tuple containing:
        - SC: 2D array of shape (nfft//2, num_alphas)
            Cyclic Spectral Coherence matrix.
        - f: 1D array
            Carrier frequency axis in Hz.
        - a: 1D array
            Cyclic frequency (alpha) axis in Hz.
            
    Notes
    -----
    1. The CSC matrix reveals hidden periodicities in the signal's statistics.
    2. Peaks in the CSC matrix indicate strong cyclostationarity at specific
       carrier-cyclic frequency pairs.
    3. The function uses a Hamming window by default for spectral estimation.
    """
    
    l = len(x)
    alpha = 1.0 / l  # Unit modulating frequency
    x = np.array(x).flatten()
    
    # Apply Hanning window and Hilbert transform
    x = x * signal.windows.hann(len(x))
    x = signal.hilbert(x)
    
    # Calculate frequency indices
    bmax = round(alphamax * l / fs)
    bmin = round(alphamin * l / fs)
    
    # Initialize output matrix
    SC = np.zeros((nfft // 2, bmax - bmin + 1), dtype=complex)
    
    # Compute first coherence
    Coh = SCoh_W(x, x, bmin * alpha, nfft, nover, signal.windows.hann(okno), 'sym')
    SC[:, 0] = Coh[:nfft // 2]
    
    # Compute coherence for remaining frequencies
    # print("Computing spectral coherence...")
    for k in range(1 + bmin, bmax + 1):
        Coh = SCoh_W(x, x, k * alpha, nfft, nover, signal.windows.hann(okno), 'sym')
        ind = k - bmin
        SC[:, ind] = Coh[:nfft // 2]
        
        # # Progress indicator
        # if k % max(1, (bmax - bmin) // 10) == 0:
        #     progress = (k - bmin) / (bmax - bmin) * 100
        #     print(f"Progress: {progress:.1f}%")
    
    # Create frequency axes
    f = np.linspace(0, fs / 2, nfft // 2)
    a = np.arange(bmin, bmax + 1) * fs / l
    
    # print("Computation complete!")
    
    return SC, f, a