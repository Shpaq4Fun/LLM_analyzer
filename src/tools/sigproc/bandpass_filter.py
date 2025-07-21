import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

def bandpass_filter(
    data: np.ndarray,
    output_image_path: str,
    lowcut_freq: float = 1000,
    highcut_freq: float = 4000,
    order: int = 4
) -> np.ndarray:
    """
    Applies a zero-phase band-pass Butterworth filter to a signal.

    Args:
        signal_data (np.ndarray): 1D NumPy array containing the time-series signal.
        sampling_rate (int): The sampling frequency of the signal in Hz.
        lowcut_freq (float): The lower cutoff frequency for the filter in Hz.
        highcut_freq (float): The upper cutoff frequency for the filter in Hz.
        order (int, optional): The order of the Butterworth filter. A higher order
                               provides a steeper cutoff. Defaults to 4.

    Returns:
        np.ndarray: The band-pass filtered 1D signal. Returns the original signal
                    if the frequency range is invalid.
    """
    signal_data = data.get('signal_data')
    if signal_data is None:
        print("Warning: No signal data provided for create_signal_spectrogram tool.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_signal_spectrogram tool.")

    # --- Filter Design ---
    # Nyquist frequency is half the sampling rate
    nyquist_freq = 0.5 * sampling_rate

    # --- Input Validation ---
    if lowcut_freq >= highcut_freq:
        print(f"Warning: Lowcut frequency ({lowcut_freq} Hz) is greater than or equal to highcut frequency ({highcut_freq} Hz). Returning original signal.")
        return signal_data
    if highcut_freq >= nyquist_freq:
        print(f"Warning: Highcut frequency ({highcut_freq} Hz) is greater than or equal to the Nyquist frequency ({nyquist_freq} Hz). Clipping highcut to Nyquist region.")
        highcut_freq = nyquist_freq - 1 # Set just below Nyquist to be safe
    if lowcut_freq <= 0:
        print(f"Warning: Lowcut frequency ({lowcut_freq} Hz) is non-positive. Clipping lowcut to a small positive value.")
        lowcut_freq = 0.1 # A small positive number

    # Normalize the cutoff frequencies
    low = lowcut_freq / nyquist_freq
    high = highcut_freq / nyquist_freq

    # Get the filter coefficients
    b, a = butter(order, [low, high], btype='band', analog=False)

    # --- Apply the filter ---
    # Use filtfilt for a zero-phase filter (no time delay)
    filtered_signal = filtfilt(b, a, signal_data)

    time_axis = np.arange(len(signal_data)) / sampling_rate

    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    plt.plot(time_axis, filtered_signal, color="#001A52", linewidth=0.5)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title('Signal after bandpass filtration of order {} in range [{}, {}] Hz'.format(order,lowcut_freq, highcut_freq))
    plt.xlim(0, time_axis[-1])
    plt.axis('tight')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()


    results = {
        'filtered_signal': filtered_signal,
        'domain': 'time-series',
        'primary_data': 'filtered_signal',
        'sampling_rate': sampling_rate,
        'image_path': output_image_path
    }
    return results
