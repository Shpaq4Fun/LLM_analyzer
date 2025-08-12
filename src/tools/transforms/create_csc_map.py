import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os, pickle

def create_csc_map(
        data: dict,
        output_image_path: str,
        min_alpha: int = 1,
        max_alpha: int = 150,
        window: int = 256,
        overlap: int = 220,
) -> dict:
    """
    Compute and save the Cyclic Spectral Coherence (CSC) map for a signal.

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the array key holding the input signal
    - sampling_rate: int, sampling frequency in Hz

    Other parameters:
    - min_alpha, max_alpha: range of cyclic (modulating) frequencies [Hz]
    - window: window length used for analysis (and nfft)
    - overlap: number of overlapping samples between windows

    Returns:
    - dict with keys:
        cyclic_frequencies, carrier_frequencies, csc_map, domain ('bi-frequency-matrix'),
        primary_data, secondary_data, tertiary_data, sampling_rate, original_signal_data,
        image_path
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
        # plt.contourf(cyclic_frequencies, carrier_frequencies, csc_map, levels=20, cmap='viridis')
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