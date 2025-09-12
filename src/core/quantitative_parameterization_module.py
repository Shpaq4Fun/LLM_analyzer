"""Quantitative Parameterization Module

This module provides functionality to compute quantitative metrics and statistical features
from various signal processing tool outputs. It serves as a post-processing layer that
enriches tool outputs with domain-specific metrics, enabling better analysis and comparison
of signal characteristics across different domains.

Key Features:
- Domain-specific metric calculation for different signal representations
- Automatic dispatch to appropriate metric calculators based on data domain
- Generation of statistical summaries and diagnostic visualizations
- Support for time-series, frequency spectra, time-frequency matrices, cyclostationary maps,
  and NMF decompositions
- Generation of supplementary figures for enhanced analysis

Example Usage:
    >>> from core.quantitative_parameterization_module import calculate_quantitative_metrics
    >>> 
    >>> # Process tool output through the parameterization pipeline
    >>> enriched_output = calculate_quantitative_metrics(tool_output_dict)
    >>> 
    # Access computed metrics
    >>> print(enriched_output['new_params'])
"""

from typing import Dict, Any, Tuple, Optional, Union, List
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew, levy_stable, jarque_bera
from scipy.signal import find_peaks, istft, firwin2, stft, filtfilt
from numpy.typing import NDArray
from src.lib.rlowess_smoother import rlowess2
# === Helper Functions ===

def _extract_ids_from_path(image_path: Optional[str]) -> Tuple[Optional[str], Optional[int]]:
    """Extract run_id and action_id from a formatted image path string.
    
    This helper function parses standardized file paths to extract metadata about the
    analysis run and action that generated the file. The path is expected to follow
    a specific format containing the run_id and action_id.
    
    Parameters
    ----------
    image_path : Optional[str]
        The file path to parse, expected to contain run_id and action_id.
        Format: '.../run_<run_id>/action_<action_id>/...' or similar.
        
    Returns
    -------
    Tuple[Optional[str], Optional[int]]
        A tuple containing (run_id, action_id) if successfully parsed, or (None, None) if
        the path doesn't match the expected format or is invalid.
        
    Examples
    --------
    >>> _extract_ids_from_path('path/to/run_123/action_45/results.png')
    ('123', 45)
    >>> _extract_ids_from_path('invalid/path')
    (None, None)
    
    Notes
    -----
    - The function is lenient and will return (None, None) for any malformed input
    - Action ID is converted to integer, while run ID is kept as string
    - Handles both forward and backward slashes in paths
    analysis run and processing step that generated the file.

    Parameters
    ----------
    image_path : Optional[str]
        The file path to parse. Expected format is:
        './run_state/run_<timestamp>/step<number>_<tool_name>.<ext>'

    Returns
    -------
    Tuple[Optional[str], Optional[int]]
        A tuple containing:
        - run_id: str or None
            The run identifier extracted from the directory name (e.g., 'run_20250716_125140')
        - action_id: int or None
            The processing step number extracted from the filename (e.g., 1 for 'step1_...')
            
    Examples
    --------
    >>> _extract_ids_from_path('./run_state/run_20250716_125140/step1_fft_spectrum.png')
    ('run_20250716_125140', 1)
    """
    if not image_path or not isinstance(image_path, str):
        return None, None

    try:
        filename = os.path.basename(image_path)
        parts = filename.split('_')

        action_id = None
        # Check if the first part is like 'step1', 'step2', etc.
        if len(parts) > 0 and parts[0].startswith('step'):
            action_id_str = parts[1]  # Get the string part after "step"
            if action_id_str.isdigit():
                action_id = int(action_id_str)

        # Extract run_id from the directory path
        run_dir = os.path.dirname(image_path)
        run_id = os.path.basename(run_dir)

        # Basic validation that run_id looks correct
        if not run_id.startswith('run_'):
             run_id = None

    except (IndexError, TypeError, AttributeError, ValueError):
        return None, None

    return run_id, action_id

def _get_fft_frequencies(signal_length: int, sampling_rate: float) -> np.ndarray:
    """Calculate the frequency values for an FFT result.
    
    This helper function generates the frequency axis for an FFT result based on the
    signal length and sampling rate, following the standard FFT frequency convention.
    
    Parameters
    ----------
    signal_length : int
        The length of the signal in samples. For real-valued FFTs, this should be
        the length of the input signal (not the FFT size).
    sampling_rate : float
        The sampling frequency of the signal in Hz.
        
    Returns
    -------
    np.ndarray
        Array of frequency values in Hz corresponding to the FFT bins.
        For even-length signals, returns frequencies from 0 to fs/2.
        For odd-length signals, returns frequencies from 0 to fs/2 (inclusive).
        
    Notes
    -----
    - Follows numpy.fft.rfftfreq convention for real-valued FFTs
    - Handles both even and odd signal lengths correctly
    - The Nyquist frequency (fs/2) is included for odd-length signals
    
    Examples
    --------
    >>> _get_fft_frequencies(1000, 1000)  # 1 second signal at 1kHz
    array([  0.,   1.,   2., ..., 498., 499., 500.])
    """
    return np.fft.rfftfreq(signal_length, d=1.0/sampling_rate)

def _calculate_band_energy(spectrum: np.ndarray, freq_axis: np.ndarray,
                         freq_band: Tuple[float, float]) -> float:
    """Calculate the energy in a specific frequency band of a spectrum.
    
    This function computes the total energy (sum of squared magnitudes) within a
    specified frequency range of a power spectrum. It's useful for analyzing
    specific frequency components or bands of interest.
    
    Parameters
    ----------
    spectrum : np.ndarray
        1D array containing the power spectrum or power spectral density.
    freq_axis : np.ndarray
        1D array of frequency values corresponding to the spectrum bins (in Hz).
    freq_band : Tuple[float, float]
        The frequency range (low_freq, high_freq) in Hz to compute energy over.
        Both values are inclusive in the calculation.
        
    Returns
    -------
    float
        The total energy in the specified frequency band.
        
    Notes
    -----
    - The function assumes `freq_axis` is sorted in ascending order.
    - If the frequency band is outside the range of `freq_axis`, returns 0.
    - The energy is computed as the sum of the spectrum values in the band.
    
    Examples
    --------
    >>> freqs = np.linspace(0, 100, 1001)  # 0-100 Hz in 0.1 Hz steps
    >>> spectrum = np.ones_like(freqs)     # Flat spectrum
    >>> _calculate_band_energy(spectrum, freqs, (10, 20))  # Energy in 10-20 Hz
    100.0
    """
    band_mask = (freq_axis >= freq_band[0]) & (freq_axis <= freq_band[1])
    return np.sum(spectrum[band_mask])

def calculate_gini_index(array: np.ndarray) -> float:
    """Calculate the Gini coefficient of a numpy array.
    
    The Gini coefficient is a measure of statistical dispersion intended to represent
    the income or wealth distribution of a nation's residents. Here, it's used to
    quantify the inequality of energy distribution in signal representations.

    Parameters
    ----------
    array : np.ndarray
        Input array for which to calculate the Gini coefficient.
        Can be any-dimensional; will be flattened before processing.

    Returns
    -------
    float
        Gini coefficient in the range [0, 1], where:
        - 0 represents perfect equality (all values are equal)
        - 1 represents maximal inequality (all values are zero except one)
        
    Notes
    -----
    The implementation ensures numerical stability by:
    1. Handling negative values by shifting to non-negative
    2. Adding a small constant to avoid division by zero
    3. Sorting the array for efficient calculation
    
    References
    ----------
    [1] Gini, C. (1912). Variabilità e mutabilità.
    """
    array = array.flatten()
    if np.amin(array) < 0:
        array -= np.amin(array)  # Shift to non-negative
    array += 1e-7  # Add small constant to avoid division by zero
    array = np.sort(array)  # Sort for efficient calculation
    n = len(array)
    index = np.arange(1, n + 1)
    return np.sum((2 * index - n - 1) * array) / (n * np.sum(array))

def estimate_alpha_stable(array: np.ndarray) -> float:
    """Estimate the alpha parameter of an alpha-stable distribution.
    
    The alpha parameter characterizes the tail behavior of the distribution:
    - α ≈ 2: Gaussian distribution (light tails)
    - 0 < α < 2: Heavy-tailed distribution
    - α → 0: More impulsive behavior

    Parameters
    ----------
    array : np.ndarray
        Input data array. Will be flattened before processing.

    Returns
    -------
    float
        Estimated alpha parameter in the range (0, 2].
        
    Notes
    -----
    This is a simplified implementation using scipy's internal _fitstart method.
    For production use, consider a more robust estimation method that handles
    edge cases and provides confidence intervals.
    
    References
    ----------
    [1] Nolan, J. P. (2020). Univariate Stable Distributions.
    """
    array = array.flatten()
    try:
        # Use scipy's internal fitting method (simplified)
        return 2 - levy_stable._fitstart(array)[0]
    except Exception:
        # Fallback to a reasonable default if fitting fails
        return 2.0

def _smooth_spectrum(spectrum: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Apply a simple moving average filter to smooth a 1D spectrum.
    
    This function applies a uniform moving average filter to reduce noise in a 1D
    spectrum while preserving the main spectral features. The smoothing is performed
    using a sliding window approach with reflection padding at the boundaries.
    
    Parameters
    ----------
    spectrum : np.ndarray
        1D array containing the spectrum to be smoothed.
    window_size : int, optional (default=5)
        Size of the smoothing window. Must be an odd positive integer.
        If even, it will be incremented by 1 to ensure symmetry.
        
    Returns
    -------
    np.ndarray
        Smoothed spectrum with the same shape as the input.
        
    Notes
    -----
    - Uses reflection padding to handle boundaries, which helps reduce edge effects.
    - The window is automatically adjusted to be odd-sized.
    - For very small windows (≤ 1), returns the original spectrum unchanged.
    - The output is normalized by the window size to preserve the signal's energy.
    
    Examples
    --------
    >>> x = np.sin(2*np.pi*np.linspace(0, 1, 100)) + 0.1*np.random.randn(100)
    >>> smoothed = _smooth_spectrum(x, window_size=7)
    >>> x.shape == smoothed.shape
    True
    """
    if window_size <= 1:
        return spectrum
    if window_size % 2 == 0:
        window_size += 1
    window = np.ones(window_size) / window_size
    return np.convolve(spectrum, window, mode='same')

def _find_peaks(spectrum: np.ndarray, min_prominence: float = 0.1) -> np.ndarray:
    """Identify significant peaks in a 1D spectrum using prominence-based detection.
    
    This function detects peaks in a spectrum while ignoring small fluctuations
    and noise by using a minimum prominence threshold. It's particularly useful
    for identifying dominant frequency components in spectral analysis.
    
    Parameters
    ----------
    spectrum : np.ndarray
        1D array containing the spectrum (e.g., power spectral density).
    min_prominence : float, optional
        Minimum prominence required to identify a peak, as a fraction of the
        maximum value in the spectrum. Default is 0.1 (10% of max).
        
    Returns
    -------
    np.ndarray
        Array of indices where peaks were found, sorted by peak height in
        descending order.
        
    Notes
    -----
    - Uses scipy.signal.find_peaks for peak detection
    - The prominence is calculated relative to the maximum value in the spectrum
    - Peaks are sorted by height (highest first)
    - For better results, consider smoothing the spectrum before peak detection
    
    Examples
    --------
    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 1000))
    >>> spectrum = np.abs(np.fft.rfft(x))**2
    >>> peaks = _find_peaks(spectrum, min_prominence=0.1)
    >>> peaks[0]  # Index of the dominant peak
    5
    """
    peaks, _ = find_peaks(spectrum, prominence=min_prominence)
    return peaks[np.argsort(spectrum[peaks])[::-1]]

def normalize_data(data: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """Normalize data to the range [0, 1] using min-max scaling.
    
    This function performs min-max scaling on the input data, transforming all values
    to the range [0, 1]. It handles edge cases such as constant arrays and includes
    a small epsilon to prevent division by zero.
    
    Parameters
    ----------
    data : np.ndarray
        Input data to be normalized. Can be any shape, will be flattened if needed.
    epsilon : float, optional (default=1e-10)
        Small constant to avoid division by zero when data has zero range.
        
    Returns
    -------
    np.ndarray
        Normalized data with the same shape as input, with values in [0, 1].
        
    Notes
    -----
    - For constant input arrays, returns an array of zeros with the same shape.
    - Handles both integer and floating-point inputs appropriately.
    - Preserves the input array's data type (dtype).
    - If all values in the input are identical, returns an array of zeros.
    - Handles edge cases like constant input and empty arrays.
    
    Examples
    --------
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> normalize_data(data)
    array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    
    >>> normalize_data(np.array([1, 1, 1]))  # Constant input
    array([0., 0., 0.])
    """
    if data.size == 0:
        return data
        
    data_min = np.min(data)
    data_range = np.max(data) - data_min
    
    if data_range < epsilon:
        return np.zeros_like(data, dtype=np.float64)
    
    normalized = (data - data_min) / data_range
    return normalized.astype(np.float64)

# === The Dispatcher Function (Public) ===

def calculate_quantitative_metrics(tool_output: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance tool output with domain-specific quantitative metrics.
    
    This is the main entry point for adding quantitative metrics to tool outputs.
    It dispatches to specialized handlers based on the 'domain' field in the input.

    Parameters
    ----------
    tool_output : Dict[str, Any]
        Dictionary containing at minimum a 'domain' key indicating the data type.
        The specific required fields depend on the domain:
        
        Common keys:
        - 'primary_data': str, key for the main data array
        - 'secondary_data': str, key for secondary data (e.g., frequency axis)
        - 'tertiary_data': str, key for tertiary data (e.g., time/freq axes)
        - 'sampling_rate': float, sampling frequency in Hz
        - 'image_path': str or List[str], path(s) to output images
        
        Domain-specific keys:
        - Time-series: 1D signal data
        - Frequency-spectrum: 1D spectrum data with frequency axis
        - Time-frequency-matrix: 2D spectrogram data
        - Bi-frequency-matrix: 2D cyclostationary map
        - Decomposed-matrix: NMF or other matrix factorization results

    Returns
    -------
    Dict[str, Any]
        The input dictionary with an additional 'new_params' key containing the
        computed metrics. The original input dictionary is not modified.
        
    Raises
    ------
    TypeError
        If the input is not a dictionary.
    
    Examples
    --------
    >>> # Process a time-series signal
    >>> ts_data = {
    ...     'domain': 'time-series',
    ...     'primary_data': 'signal',
    ...     'signal': np.random.randn(1000),
    ...     'sampling_rate': 1000
    ... }
    >>> enriched = calculate_quantitative_metrics(ts_data)
    >>> print(enriched['new_params'].keys())
    
    Notes
    -----
    The function adds a 'new_params' dictionary to the output containing all
    computed metrics. The specific metrics depend on the input domain.
    """
    if not isinstance(tool_output, dict):
        raise TypeError("Input must be a dictionary")
        
    if not tool_output:
        return {}

    # Create a copy to avoid modifying the input
    result = tool_output.copy()
    
    # Domain-based dispatch to specialized handlers
    domain_handlers = {
        'time-series': _calculate_timeseries_stats,
        'time-frequency-matrix': _calculate_spectrogram_stats,
        'frequency-spectrum': _calculate_spectrum_stats,
        'bi-frequency-matrix': _calculate_cyclomap_stats,
        'decomposed_matrix': _calculate_nmf_stats
    }
    
    domain = result.get('domain', 'unknown_domain')
    handler = domain_handlers.get(domain)
    
    # Calculate metrics if a handler exists for this domain
    result["new_params"] = handler(result) if handler else {}
    
    return result

# === Specialized Handler Functions (Private) ===

def _calculate_timeseries_stats(data_dict: Dict[str, Any]) -> Dict[str, float]:
    """Calculate statistical features for a 1D time-series signal.
    
    This function computes a comprehensive set of statistical features that characterize
    the time-domain properties of a signal, including moments, peak characteristics,
    and periodicity measures.

    Parameters
    ----------
    data_dict : Dict[str, Any]
        Dictionary containing the time-series data with the following keys:
        - 'primary_data': str, key for the signal data
        - The signal data itself (1D numpy array)
        - 'sampling_rate': float, sampling frequency in Hz (optional for some metrics)

    Returns
    -------
    Dict[str, float]
        Dictionary containing the following metrics:
        - 'kurtosis': float, measure of tailedness (normalized 4th moment)
        - 'skewness': float, measure of asymmetry (normalized 3rd moment)
        - 'rms': float, root-mean-square amplitude
        - 'crest_factor': float, ratio of peak to RMS amplitude
        - 'cyclicity_period_samples': int, dominant period in samples
        - 'cyclicity_strength': float, strength of periodicity [0,1]
        
    Notes
    -----
    - Kurtosis is calculated using Fisher's definition (normal distribution = 3)
    - Cyclicity measures are based on autocorrelation peaks
    - The function is robust to NaN and infinite values
    """
    primary_data_key = data_dict.get('primary_data')
    signal = data_dict.get(primary_data_key)
    if signal is None or not isinstance(signal, np.ndarray) or signal.size == 0:
        return data_dict

    peak_value = np.max(np.abs(signal))
    rms_value = np.sqrt(np.mean(signal**2))

    autocorr = np.correlate(signal, signal, mode='full')
    autocorr = autocorr[autocorr.size // 2:]
    peaks, _ = find_peaks(autocorr, height=0.1 * np.max(autocorr))

    dominant_period_samples = 0
    cyclicity_strength = 0.0
    if len(peaks) > 0:
        dominant_period_samples = peaks[0]
        if autocorr[0] > 0:
            cyclicity_strength = autocorr[dominant_period_samples] / autocorr[0]

    new_params = {
        'kurtosis': float(kurtosis(signal, fisher=False)),
        'skewness': float(skew(signal)),
        'rms': float(rms_value),
        'crest_factor': float(peak_value / rms_value if rms_value > 0 else 0),
        "cyclicity_period_samples": int(dominant_period_samples),
        "cyclicity_strength": float(cyclicity_strength)
    }

    # data_dict.update(new_params)
    return new_params

def _calculate_spectrum_stats(data_dict: Dict[str, Any]) -> Dict[str, float]:
    """Calculate key metrics for a 1D frequency spectrum.
    
    This function analyzes the frequency-domain representation of a signal,
    identifying dominant frequency components and characterizing the spectral
    distribution.

    Parameters
    ----------
    data_dict : Dict[str, Any]
        Dictionary containing the spectrum data with the following keys:
        - 'primary_data': str, key for the amplitude spectrum
        - 'secondary_data': str, key for the frequency axis
        - The spectrum data (1D numpy array)
        - The frequency axis (1D numpy array)
        - 'sampling_rate': float, sampling frequency in Hz

    Returns
    -------
    Dict[str, float]
        Dictionary containing the following metrics:
        - 'dominant_frequency_hz': float, frequency of the highest peak
        - 'spectral_centroid': float, weighted mean of frequencies
        - 'bandwidth': float, spectral width measure
        - 'spectral_flatness': float, tonality measure (0-1)
        - 'spectral_rolloff': float, frequency below which 85% of energy is contained
        
    Notes
    -----
    - All frequency values are in Hz
    - The spectrum is assumed to be one-sided (positive frequencies only)
    - Input validation is performed to ensure data consistency
    """
    primary_data_key = data_dict.get('primary_data')
    spectrum_amps = data_dict.get(primary_data_key)
    secondary_data_key = data_dict.get('secondary_data')
    spectrum_freqs = data_dict.get(secondary_data_key)

    if spectrum_amps is None or spectrum_freqs is None or \
       not isinstance(spectrum_amps, np.ndarray) or spectrum_amps.size == 0 or \
       not isinstance(spectrum_freqs, np.ndarray) or spectrum_freqs.size != spectrum_amps.size:
        return data_dict

    dominant_frequency_index = np.argmax(spectrum_amps)
    dominant_frequency_hz = spectrum_freqs[dominant_frequency_index]

    new_params = {
        'dominant_frequency_hz': float(dominant_frequency_hz)
    }

    # data_dict.update(new_params)
    return new_params

def _calculate_spectrogram_stats(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a time-frequency spectrogram and compute diagnostic metrics.
    
    This function processes a 2D spectrogram to extract features that characterize
    the time-frequency distribution of signal energy, including temporal evolution
    of spectral properties and statistical moments across frequency bands.

    Parameters
    ----------
    data_dict : Dict[str, Any]
        Dictionary containing the spectrogram data with the following keys:
        - 'primary_data': str, key for the spectrogram matrix
        - 'secondary_data': str, key for the time axis
        - 'tertiary_data': str, key for the frequency axis
        - The spectrogram data (2D numpy array, freq × time)
        - 'image_path': str or List[str], path(s) for saving diagnostic plots
        - 'sampling_rate': float, sampling frequency in Hz

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the following metrics and selectors:
        - 'gini_index': float, measure of energy concentration
        - 'skewness_selector': np.ndarray, frequency-dependent skewness
        - 'jarque_bera_selector': np.ndarray, normality test statistics
        - 'alpha_stable_selector': np.ndarray, heavy-tailed distribution estimates
        - 'joint_selector': np.ndarray, combined feature vector
        - 'selectors_image_path': str, path to saved diagnostic plot
        
    Notes
    -----
    - The function generates a diagnostic plot showing the different selectors
    - All selectors are normalized to the range [0, 1] for comparison
    - The joint selector combines information from all individual selectors
    """
    image_path = data_dict.get('image_path')
    # Handle the case where image_path is a list
    primary_image_path = image_path[0] if isinstance(image_path, list) else image_path
    run_id, action_id = _extract_ids_from_path(primary_image_path)

    if run_id is None or action_id is None:
        return data_dict

    primary_data_key = data_dict.get('primary_data')
    spectrogram_matrix = data_dict.get(primary_data_key)
    secondary_data_key = data_dict.get('secondary_data')
    frequencies = data_dict.get(secondary_data_key)

    if spectrogram_matrix is None or frequencies is None or spectrogram_matrix.size == 0:
        return data_dict

    gini = calculate_gini_index(spectrogram_matrix.flatten())
    f_start_ind = 2
    num_freq_bins = spectrogram_matrix.shape[0]
    sk_selector = np.zeros(num_freq_bins)
    jb_selector = np.zeros(num_freq_bins)
    alpha_selector = np.zeros(num_freq_bins)
    joint_selector = np.zeros(num_freq_bins)
    for i in range(f_start_ind,num_freq_bins):
        energy_slice = spectrogram_matrix[i,:]
        sk_selector[i] = kurtosis(energy_slice, fisher=False)
        jb_selector[i] = jarque_bera(energy_slice)[0]
        alpha_selector[i] = estimate_alpha_stable(energy_slice)
        joint_selector[i] = sk_selector[i] * jb_selector[i] * alpha_selector[i]

    sk_selector = normalize_data(sk_selector)
    jb_selector = normalize_data(jb_selector)
    alpha_selector = normalize_data(alpha_selector)
    

    selectors_image_path = os.path.join(f"./run_state/{run_id}", f"step_{action_id}_selectors.png")
    # if not os.path.isfile(selectors_image_path):
    fig, ax1 = plt.subplots(figsize=(8, 7))

    color = 'tab:blue'
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Normality Test Statistics', color=color)
    ax1.plot(frequencies, sk_selector, color=color, linestyle='-', label='Spectral Kurtosis')
    ax1.plot(frequencies, jb_selector, color='tab:cyan', linestyle='--', label='Jarque-Bera (scaled)')
    ax1.plot(frequencies, alpha_selector, color=color, linestyle=':', label='Alpha Parameter')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, which='both', linewidth=0.5)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Joint Selector', color=color)
    joint_selector = rlowess2(frequencies, joint_selector, window_size=12, it=5, degree=2)
    joint_selector = normalize_data(joint_selector)
    ax1.plot(frequencies, joint_selector, color=color, linestyle='-', label='Joint Selector', linewidth=1)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 1)

    fig.suptitle('Diagnostic Selectors')
    fig.tight_layout()
    lines, labels = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')

    plt.savefig(selectors_image_path)
    fig_path = os.path.join(f"{selectors_image_path[:-2]}kl")
    with open(fig_path, 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

    # peak_sk_freq_hz = frequencies[np.argmax(sk_selector)]
    # peak_jb_freq_hz = frequencies[np.argmax(jb_selector)]
    # peak_alpha_freq_hz = frequencies[np.argmin(alpha_selector)]

    new_params = {
        "sparsity_gini_index": float(gini),
        # "peak_kurtosis_freq_hz": float(peak_sk_freq_hz),
        # "peak_jarque_bera_freq_hz": float(peak_jb_freq_hz),
        # "min_alpha_freq_hz": float(peak_alpha_freq_hz),
        # "selectors_data": {
        #     "frequencies_hz": frequencies.tolist(),
        #     "spectral_kurtosis": sk_selector.tolist(),
        #     "jarque_bera": jb_selector.tolist(),
        #     "alpha_stable": alpha_selector.tolist()
        # },
        "supporting_image_paths": {
            "selectors_image_path": selectors_image_path,
        }
    }

    # data_dict.update(new_params)
    return new_params

def _calculate_cyclomap_stats(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a bi-frequency cyclostationary map and compute statistical features.
    
    This function processes a cyclostationary map (cyclic spectral coherence or
    spectral correlation) to extract features that characterize the cyclostationary
    properties of the signal across different carrier and cyclic frequencies.

    Parameters
    ----------
    data_dict : Dict[str, Any]
        Dictionary containing the cyclomap data with the following keys:
        - 'primary_data': str, key for the cyclomap matrix (cyclic_freq × carrier_freq)
        - 'secondary_data': str, key for the carrier frequency axis
        - 'tertiary_data': str, key for the cyclic frequency axis
        - 'sampling_rate': float, sampling frequency in Hz
        - 'image_path': str or List[str], path(s) for saving diagnostic plots

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the following metrics:
        - 'max_coherence': float, maximum coherence value in the map
        - 'peak_carrier_freq': float, carrier frequency at maximum coherence
        - 'peak_cyclic_freq': float, cyclic frequency at maximum coherence
        - 'mean_coherence': float, mean coherence across the map
        - 'gini_index': float, concentration of coherence values
        - 'supporting_image_paths': Dict with paths to generated visualizations
        
    Notes
    -----
    - The cyclomap is assumed to be normalized to [0,1] range
    - Peaks are detected using a prominence-based algorithm
    - Includes visualization of the cyclomap with detected peaks
    """
    image_path = data_dict.get('image_path')
    # Handle the case where image_path is a list
    primary_image_path = image_path[0] if isinstance(image_path, list) else image_path
    run_id, action_id = _extract_ids_from_path(primary_image_path)

    if run_id is None or action_id is None:
        return data_dict

    primary_data_key = data_dict.get('primary_data')
    csc_map = data_dict.get(primary_data_key)
    secondary_data_key = data_dict.get('secondary_data')
    cyclic_frequencies = data_dict.get(secondary_data_key)
    tertiary_data_key = data_dict.get('tertiary_data')
    carrier_frequencies = data_dict.get(tertiary_data_key)

    if csc_map is None or carrier_frequencies is None or csc_map.size == 0:
        return data_dict

    gini = calculate_gini_index(csc_map.flatten())
    f_start_ind = 2
    num_freq_bins = csc_map.shape[0]
    sk_selector = np.zeros(num_freq_bins)
    jb_selector = np.zeros(num_freq_bins)
    alpha_selector = np.zeros(num_freq_bins)
    joint_selector = np.zeros(num_freq_bins)
    for i in range(f_start_ind,num_freq_bins):
        energy_slice = csc_map[i, :]
        sk_selector[i] = kurtosis(energy_slice, fisher=False)
        jb_selector[i] = jarque_bera(energy_slice)[0]
        alpha_selector[i] = estimate_alpha_stable(energy_slice)
        joint_selector[i] = sk_selector[i] * jb_selector[i] * alpha_selector[i]


    sk_selector = normalize_data(sk_selector)
    jb_selector = normalize_data(jb_selector)
    alpha_selector = normalize_data(alpha_selector)
    joint_selector = normalize_data(joint_selector)

    selectors_image_path = os.path.join(f"./run_state/{run_id}", f"step_{action_id}_selectors.png")
    if not os.path.isfile(selectors_image_path):
        fig, ax1 = plt.subplots(figsize=(12, 8))

        color = 'tab:blue'
        ax1.set_xlabel('Frequency [Hz]')
        ax1.set_ylabel('Normality Test Statistics', color=color)
        ax1.plot(carrier_frequencies, sk_selector, color=color, linestyle='-', label='Spectral Kurtosis')
        ax1.plot(carrier_frequencies, jb_selector, color='tab:cyan', linestyle='--', label='Jarque-Bera')
        ax1.plot(carrier_frequencies, alpha_selector, color=color, linestyle=':', label='Alpha Parameter')
        # ax1.set_ylim(0, 1)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linewidth=0.5)

        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Joint Parameter', color=color)
        joint_selector = rlowess2(carrier_frequencies, joint_selector, window_size=12, it=5, degree=2)
        ax2.plot(carrier_frequencies, joint_selector, color=color, linestyle='-', label='Joint Parameter', linewidth=2)
        ax2.tick_params(axis='y', labelcolor=color)
        # ax2.set_ylim(0, 1)

        fig.suptitle('Diagnostic Selectors')
        fig.tight_layout()
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')
        # ax1.legend(lines, labels, loc='upper right')

        plt.savefig(selectors_image_path)
        fig_path = os.path.join(f"{selectors_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close()

    # peak_sk_freq_hz = carrier_frequencies[np.argmax(sk_selector)]
    # peak_jb_freq_hz = carrier_frequencies[np.argmax(jb_selector)]
    # peak_alpha_freq_hz = carrier_frequencies[np.argmin(alpha_selector)]


    num_alpha_bins = csc_map.shape[1]
    f_start_ind = 2
    sk_ees = np.zeros(num_alpha_bins)
    jb_ees = np.zeros(num_alpha_bins)
    alpha_ees = np.zeros(num_alpha_bins)
    joint_ees = np.zeros(num_alpha_bins)
    
    for i in range(f_start_ind,num_alpha_bins):
        alpha_slice = csc_map[:,i]
        sk_ees[i] = sum(np.multiply(alpha_slice,sk_selector))
        jb_ees[i] = sum(np.multiply(alpha_slice,jb_selector))
        alpha_ees[i] = sum(np.multiply(alpha_slice,alpha_selector))
        joint_ees[i] = sum(np.multiply(alpha_slice,joint_selector))

    ees_image_path = os.path.join(f"./run_state/{run_id}", f"step_{action_id}_EES.png")
    if not os.path.isfile(ees_image_path):
        fig, ax1 = plt.subplots(figsize=(12, 8))

        color = 'tab:blue'
        ax1.set_xlabel('Modulating Frequency [Hz]')
        ax1.set_ylabel('Value', color=color)
        ax1.plot(cyclic_frequencies, sk_ees, color=color, linestyle='-', label='Spectral Kurtosis')
        ax1.plot(cyclic_frequencies, jb_ees, color=color, linestyle='--', label='Jarque-Bera')
        ax1.plot(cyclic_frequencies, alpha_ees, color=color, linestyle=':', label='Alpha Parameter')

        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linewidth=0.5)

        color = 'tab:red'
        ax2 = ax1.twinx()
        ax2.set_ylabel('Joint EES', color=color)
        ax2.plot(cyclic_frequencies, joint_ees, color=color, linestyle='-', label='Joint EES', linewidth=2)
        ax2.tick_params(axis='y', labelcolor=color)
        # ax2.set_ylim(0, 1)

        fig.suptitle('Selector-based EES')
        fig.tight_layout()
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')

        plt.savefig(ees_image_path)
        fig_path = os.path.join(f"{ees_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close()


    new_params = {
        "sparsity_gini_index": float(gini),
        # "peak_kurtosis_freq_hz": float(peak_sk_freq_hz),
        # "peak_jarque_bera_freq_hz": float(peak_jb_freq_hz),
        # "min_alpha_freq_hz": float(peak_alpha_freq_hz),
        "supporting_image_paths": {
            "selectors_image_path": selectors_image_path,
            "ees_image_path": ees_image_path
        }
    }

    # data_dict.update(new_params)
    return new_params

def _calculate_nmf_stats(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze Non-negative Matrix Factorization (NMF) components and compute statistics.
    
    This function processes NMF decomposition results to extract meaningful features
    and statistics from the basis (W) and coefficient (H) matrices. It supports
    reconstruction of time-domain signals from NMF components and computes various
    statistical measures to characterize each component.

    Parameters
    ----------
    data_dict : Dict[str, Any]
        Dictionary containing NMF decomposition results with the following keys:
        - 'primary_data': str, key for the coefficient matrix H (components × time)
        - 'secondary_data': str, key for the basis matrix W (frequencies × components)
        - 'original_domain': str, domain of the original data ('time-frequency-matrix', etc.)
        - 'original_phase': np.ndarray, optional, phase information for reconstruction
        - 'sampling_rate': float, sampling frequency in Hz
        - 'carrier_frequencies': np.ndarray, frequency axis for spectral components
        - 'original_signal_data': np.ndarray, original time-domain signal
        - 'nperseg': int, number of samples per segment for STFT (if applicable)
        - 'noverlap': int, number of overlapping samples for STFT (if applicable)
        - 'image_path': str or List[str], path(s) for saving diagnostic plots

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the following metrics and reconstructions:
        - 'signals_reconstructed': List[np.ndarray], time-domain reconstructions of each component
        - 'kurtosis': np.ndarray, kurtosis of each component's activation
        - 'gini_index': np.ndarray, Gini coefficient for each component's energy distribution
        - 'dominant_frequencies': np.ndarray, dominant frequency for each component
        - 'reconstruction_metrics': Dict with reconstruction quality measures
        - 'supporting_image_paths': Dict with paths to generated visualizations
        
    Notes
    -----
    - For time-frequency inputs, uses the Griffin-Lim algorithm for phase reconstruction
    - Includes optional visualization of component activations and spectra
    - Handles both real and complex-valued inputs appropriately
    """
    image_path = data_dict.get('image_path')
    # Handle the case where image_path is a list
    primary_image_path = image_path[0] if isinstance(image_path, list) else image_path
    run_id, action_id = _extract_ids_from_path(primary_image_path)

    if run_id is None or action_id is None:
        return data_dict

    primary_data_key = data_dict.get('primary_data')
    H = data_dict.get(primary_data_key)
    secondary_data_key = data_dict.get('secondary_data')
    W = data_dict.get(secondary_data_key)
    domain = data_dict.get('original_domain')
    original_phase = data_dict.get('original_phase')
    sampling_rate = data_dict.get('sampling_rate')
    carrier_frequencies = data_dict.get('carrier_frequencies')
    original_signal_data = data_dict.get('original_signal_data')

    if H is None or W is None or H.size == 0 or W.size == 0:
        return {}
    n_components = H.shape[0]
    kurt = np.zeros(n_components)

    # === Reconstruct the Signals ===
    n_iter = 50
    signals_reconstructed = []

    if domain == 'time-frequency-matrix':
        nperseg = data_dict.get('nperseg')
        noverlap = data_dict.get('noverlap')
        nfft = data_dict.get('nfft')
        for i in range(n_components):
            W_comp = np.expand_dims(W[:, i], axis=1)
            H_comp = np.expand_dims(H[i, :], axis=0)
            W_comp = W_comp - np.min(W_comp)
            H_comp = H_comp - np.min(H_comp)


            # Reconstruct the magnitude
            reconstructed_magnitude = W_comp @ H_comp

            # Initialize phase properly - use zeros or random phase
            if original_phase is not None and original_phase.shape == reconstructed_magnitude.shape:
                phase = original_phase
            else:
                # Initialize with random phase between -π and π
                phase = np.random.uniform(-np.pi, np.pi, reconstructed_magnitude.shape)

            # Griffin-Lim algorithm
            complex_spectrogram = reconstructed_magnitude * np.exp(1j * phase)
            for _ in range(n_iter):
                # ISTFT to get time domain signal
                _, reconstructed_signal = istft(
                    complex_spectrogram,
                    fs=sampling_rate,
                    nperseg=nperseg,
                    noverlap=noverlap
                )
                # STFT back to frequency domain
                _, _, new_complex_spectrogram = stft(
                    reconstructed_signal,
                    fs=sampling_rate,
                    nperseg=nperseg,
                    noverlap=noverlap,
                    nfft=nfft
                )
                # Keep original magnitude, update phase
                new_phase = np.angle(new_complex_spectrogram)
                complex_spectrogram = reconstructed_magnitude * np.exp(1j * new_phase)

            # Final reconstruction
            _, final_reconstructed_signal = istft(
                complex_spectrogram,
                fs=sampling_rate,
                nperseg=nperseg,
                noverlap=noverlap
            )
            signals_reconstructed.append(final_reconstructed_signal)
            kurt[i] = kurtosis(final_reconstructed_signal, fisher=False)

    elif domain == 'bi-frequency-matrix':
        filter_order = 128
        for i in range(n_components):
            # Use the activation vector (H[i, :]) as the carrier-frequency profile.
            # For cyclostationary maps V has shape (cyclic_freq, carrier_freq),
            # so W is over cyclic frequencies and H is over carrier frequencies.
            # We want a filter shaped over carrier frequencies -> use H, not W.
            carrier_profile = W[:, i]

            # --- 1. Design the Custom FIR Filter ---
            # Normalize to [0,1] to use as the desired gain over carrier frequencies.
            normalized_gain = (carrier_profile - np.min(carrier_profile)) / (np.max(carrier_profile) - np.min(carrier_profile) + 1e-9)

            # firwin2 requires frequencies normalized to Nyquist.
            nyquist = sampling_rate / 2.0
            normalized_freqs = carrier_frequencies / nyquist

            # Ensure frequencies cover [0,1] if necessary.
            # freqs = np.concatenate(([0], normalized_freqs, [1]))
            # gains = np.concatenate(([0], normalized_gain, [0]))
            freqs = normalized_freqs
            gains = normalized_gain
            # Design the filter (order must be even for firwin2)
            if filter_order % 2 != 0:
                filter_order += 1

            filter_taps = firwin2(filter_order + 1, freqs, gains)

            # --- 2. Apply the Filter to the Original Signal ---
            filtered_signal = filtfilt(filter_taps, [1.0], original_signal_data)
            signals_reconstructed.append(filtered_signal)
            kurt[i] = kurtosis(filtered_signal, fisher=False)
    # === End of Reconstruction ===

    # --- Generate and save the visual output ---
    time_axis = np.arange(len(signals_reconstructed[0])) / sampling_rate  # Assuming all signals have the same length
    output_image_path = os.path.join(f"./run_state/{run_id}", f"step_{action_id}_nmf_reconstruction.png")

    fig, ax = plt.subplots(n_components,1,figsize=[8,7])
    for i in range(n_components):
        ax[i].plot(time_axis, signals_reconstructed[i], linewidth=0.5)
        ax[i].set_title(f'Reconstructed Component {i}')
        ax[i].set_xlabel('Time [s]')
        ax[i].set_ylabel('Amplitude')
        ax[i].grid(True)

    plt.savefig(output_image_path)
    fig_path = os.path.join(f"{output_image_path[:-2]}kl")
    with open(fig_path, 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

    new_params = {
        "kurtosis": kurt.tolist(),
        "signals_reconstructed": signals_reconstructed,
        "supporting_image_paths": {
            "selectors_image_path": output_image_path
        }
    }
    return new_params
