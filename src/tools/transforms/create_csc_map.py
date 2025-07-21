import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft

def create_csc_map(
        data: dict,
        output_image_path: str,
        min_alpha: int = 1,
        max_alpha: int = 200,
        nperseg: int = 256,
        overlap: int = 220,
) -> dict:
    """
    Calculates and saves the Cyclic Spectral Coherence (CSC) map for a signal.

    *** NOTE: This is a placeholder implementation for system design. ***
    It generates a synthetic CSC map with plausible features for demonstration.
    A full implementation would require a specialized cyclostationary analysis library
    and would use all the provided parameters (nperseg, overlap, nfft).

    Args:
        signal_data (np.ndarray): 1D NumPy array containing the time-series signal.
        sampling_rate (int): The sampling frequency of the signal in Hz.
        output_image_path (str): The full path where the output PNG image will be saved.
        min_alpha (int, optional): The minimum cyclic frequency (alpha) to calculate in Hz. Defaults to 1.
        max_alpha (int, optional): The maximum cyclic frequency (alpha) to calculate in Hz. Defaults to 200.
        nperseg (int, optional): The length of segments for analysis. Defaults to 256.
        overlap (int, optional): Number of overlapping points between segments. Defaults to 220.
        nfft (int, optional): Length of the FFT used for each segment. Defaults to 256.

    Returns:
        dict: A dictionary containing the results, with the following keys:
              'cyclic_frequencies' (np.ndarray): Array of cyclic frequencies (alpha).
              'carrier_frequencies' (np.ndarray): Array of carrier frequencies (f).
              'csc_map' (np.ndarray): 2D array of the CSC magnitude.
              'image_path' (str): The path where the output image was saved.
    """
    # --- Placeholder Logic to Generate a Synthetic CSC Map ---
    signal_data = data.get('signal_data')
    if signal_data is None:
        print("Warning: No signal data provided for create_fft_spectrum tool.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_fft_spectrum tool.")

    csc_map, carrier_frequencies, cyclic_frequencies = spectral_coh(signal_data[:2*sampling_rate], 
                                                                    alphamin=min_alpha, 
                                                                    alphamax=max_alpha, 
                                                                    nfft=nperseg, 
                                                                    okno=nperseg, 
                                                                    fs=sampling_rate, 
                                                                    nover=overlap)
    csc_map = np.abs(csc_map)
    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    # plt.contourf(cyclic_frequencies, carrier_frequencies, csc_map, levels=20, cmap='viridis')
    plt.pcolormesh(cyclic_frequencies, carrier_frequencies/1000, csc_map, shading='gouraud', cmap='jet_r')
    plt.ylabel('Carrier Frequency (f) [kHz]')
    plt.xlabel('Cyclic Frequency (alpha) [Hz]')
    plt.title('Cyclic Spectral Coherence (CSC) Map')
    plt.colorbar(label='Coherence Magnitude')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()

    # --- Return the structured data output ---
    results = {
        'cyclic_frequencies': cyclic_frequencies,
        'carrier_frequencies': carrier_frequencies,
        'csc_map': csc_map,
        'domain': 'bi-frequency-matrix',
        'primary_data': 'csc_map',
        'secondary_data': 'cyclic_frequencies',
        'tertiary_data': 'carrier_frequencies',
        'image_path': output_image_path
    }

    return results

def CPS_W(y, x, alpha, nfft, Noverlap, Window, opt='sym', P=None):
    """
    Welch's estimate of the (Cross) Cyclic Power Spectrum of signals y 
    and x at cyclic frequency alpha.
    
    Parameters:
    -----------
    y, x : array_like
        Input signals
    alpha : float
        Cyclic frequency (normalized by sampling frequency, 0 to 1)
    nfft : int
        FFT length
    Noverlap : int
        Number of overlapping samples
    Window : array_like or int
        Window function or window length
    opt : str, optional
        'sym' for symmetric version, 'asym' for asymmetric version
    P : float, optional
        Confidence level (between 0 and 1)
    
    Returns:
    --------
    Spec : ndarray
        Cyclic Power Spectrum
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


def SCoh_W(y, x, alpha, nfft, Noverlap, Window, opt='sym', P=None):
    """
    Welch's estimate of the Cyclic Spectral Coherence of signals y and x 
    at cyclic frequency alpha.
    
    Parameters:
    -----------
    y, x : array_like
        Input signals
    alpha : float
        Cyclic frequency (normalized by sampling frequency, 0 to 1)
    nfft : int
        FFT length
    Noverlap : int
        Number of overlapping samples
    Window : array_like or int
        Window function or window length
    opt : str, optional
        'sym' for symmetric version, 'asym' for asymmetric version
    P : float, optional
        Confidence level (between 0 and 1)
    
    Returns:
    --------
    Coh : ndarray
        Cyclic Spectral Coherence
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


def spectral_coh(x, alphamin, alphamax, nfft, okno, fs, nover):
    """
    Compute spectral coherence matrix.
    
    Parameters:
    -----------
    x : array_like
        Input signal data
    alphamin : float
        Minimum modulating frequency for computation
    alphamax : float
        Maximum modulating frequency for computation
    nfft : int
        Number of FFT points
    okno : int
        Window length
    fs : float
        Sampling frequency
    nover : int
        Number of overlapping samples
    
    Returns:
    --------
    SC : ndarray
        Output CSC matrix (nfft/2 x number_of_alphas)
    f : ndarray
        Carrier frequency axis [Hz]
    a : ndarray
        Modulating frequency axis (alpha) [Hz]
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