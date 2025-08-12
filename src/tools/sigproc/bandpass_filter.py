import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib, pickle
matplotlib.use('TkAgg')
import os
def bandpass_filter(
    data: dict,
    output_image_path: str,
    lowcut_freq: float = 1000,
    highcut_freq: float = 4000,
    order: int = 4
) -> dict:
    """
    Apply a zero-phase band-pass Butterworth filter to a signal.

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the array key holding the input signal
    - sampling_rate: int, sampling frequency in Hz
    - image_path: str, optional precomputed plot path (not used here)

    Other parameters:
    - lowcut_freq: lower cutoff frequency [Hz]
    - highcut_freq: upper cutoff frequency [Hz]
    - order: integer order of the Butterworth filter

    Returns:
    - dict with keys:
        filtered_signal (np.ndarray), domain ('time-series'), primary_data,
        sampling_rate, image_path
    """
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for create_envelope_spectrum tool.")

    signal_data = data.get(primary_data)
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
        lowcut_freq, highcut_freq = highcut_freq, lowcut_freq
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
    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        ax.plot(time_axis, filtered_signal, color="#001A52", linewidth=0.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title('Signal after bandpass filtration of order {} in range [{}, {}] Hz'.format(order,lowcut_freq, highcut_freq))
        ax.set_xlim(0, time_axis[-1])
        ax.axis('tight')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        plt.tight_layout()
        plt.savefig(output_image_path)
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close()


    results = {
        'filtered_signal': filtered_signal,
        'domain': 'time-series',
        'primary_data': 'filtered_signal',
        'sampling_rate': sampling_rate,
        'image_path': output_image_path
    }
    return results
