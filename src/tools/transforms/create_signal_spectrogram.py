import numpy as np
import scipy.signal, os
import matplotlib.pyplot as plt
import pickle
def create_signal_spectrogram(
    data: dict,
    output_image_path: str,
    window: int = 1024,
    noverlap: int = 800
) -> dict:
    """
    Calculate and save a spectrogram for a time-series signal.

    Wrapper around scipy.signal.spectrogram producing both an image and
    a structured dictionary suitable for downstream tools.

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the array key holding the input signal
    - sampling_rate: int, sampling frequency in Hz

    Other parameters:
    - window: STFT segment length
    - noverlap: overlap between segments (< window)

    Returns:
    - dict with keys:
        frequencies, times, Sxx_db (magnitude), domain ('time-frequency-matrix'),
        primary_data, secondary_data, tertiary_data, sampling_rate, nperseg,
        noverlap, original_phase, original_signal_data, image_path
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
    
    if type(window) is str:
        window = int(1024)
    if type(noverlap) is str:
        noverlap = int(800)
    # Ensure noverlap is less than window, which is a requirement for scipy
    if noverlap >= window:
        # Use a sensible default overlap if the input is invalid
        noverlap = window // 2

    # --- Internal logic uses the standard library ---
    frequencies, times, Sxx = scipy.signal.spectrogram(
        signal_data,
        fs=sampling_rate,
        window='hann',
        nperseg=window,
        noverlap=noverlap,
        nfft=2*window
    )
    phase = np.angle(Sxx)
    # Convert power to decibels for better visualization
    # Add a small epsilon to avoid log(0) errors
    Sxx_db = 10 * np.log10(np.abs(Sxx) + 1e-9)

    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        im = ax.pcolormesh(times, frequencies/1000, Sxx_db, shading='nearest', cmap='jet')
        ax.set_ylabel('Frequency [kHz]')
        ax.set_xlabel('Time [sec]')
        ax.set_title('Spectrogram')
        fig.colorbar(im, ax=ax, label='Power/Frequency (dB/Hz)')
        fig.tight_layout()
        plt.savefig(output_image_path)
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
        plt.close()  # Close the figure to free up memory

    # --- Return the structured data output ---
    results = {
        'frequencies': frequencies,
        'times': times,
        'Sxx_db': np.abs(Sxx),
        'domain': 'time-frequency-matrix',
        'primary_data': 'Sxx_db',
        'secondary_data': 'times',
        'tertiary_data': 'frequencies',
        'sampling_rate': sampling_rate,
        'nperseg': window,
        'noverlap': noverlap,
        'original_phase': phase,
        'original_signal_data': signal_data,
        'image_path': output_image_path

    }

    return results

