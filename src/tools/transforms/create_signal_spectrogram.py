import numpy as np
import scipy.signal
import matplotlib.pyplot as plt

def create_signal_spectrogram(
    data: dict,
    output_image_path: str,
    window: int = 1024,
    noverlap: int = 800
) -> dict:
    """
    Calculates and saves a spectrogram for a time-series signal.

    This function acts as a wrapper around scipy.signal.spectrogram, providing
    both a visual output (a saved image file) and a structured data output
    (a dictionary containing the raw spectrogram data).

    Args:
        data (dict): dictionary with data from previous step, with keys 
            'signal_data', 'sampling_rate' and 'output_image_path'.
        output_image_path (str): The full path where the output PNG image will be saved.
        window (int, optional): Length of each segment for the STFT. Defaults to 1024.
                                 A larger value gives better frequency resolution.
        noverlap (int, optional): Number of points to overlap between segments. 
                                  Must be less than window. Defaults to 800.

    Returns:
        dict: A dictionary containing the results, with the following keys:
              'frequencies' (np.ndarray): Array of sample frequencies.
              'times' (np.ndarray): Array of segment times.
              'Sxx_db' (np.ndarray): 2D array of the spectrogram power in dB.
              'image_path' (str): The path where the output image was saved.
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
        noverlap=noverlap
    )
    phase = np.angle(Sxx)
    # Convert power to decibels for better visualization
    # Add a small epsilon to avoid log(0) errors
    Sxx_db = 10 * np.log10(np.abs(Sxx) + 1e-9)

    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    plt.pcolormesh(times, frequencies/1000, Sxx_db, shading='gouraud', cmap='jet')
    plt.ylabel('Frequency [kHz]')
    plt.xlabel('Time [sec]')
    plt.title('Spectrogram')
    plt.colorbar(label='Power/Frequency (dB/Hz)')
    plt.tight_layout()
    plt.savefig(output_image_path)
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

