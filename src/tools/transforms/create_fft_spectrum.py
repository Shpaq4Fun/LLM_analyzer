import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

def create_fft_spectrum(
    data: dict,
    output_image_path: str
) -> dict:
    """
    Calculates and saves the Fast Fourier Transform (FFT) spectrum for a signal.

    This function provides a one-sided amplitude spectrum suitable for real-valued
    input signals, plotting the result up to the Nyquist frequency.

    Args:
        data (dict): dictionary with data from previous step, with keys 
            'signal_data', 'sampling_rate' and 'output_image_path'.
        output_image_path (str): The full path where the output PNG image will be saved.

    Returns:
        dict: A dictionary containing the results, with the following keys:
              'frequencies' (np.ndarray): Array of frequency bins in Hz.
              'amplitudes' (np.ndarray): Array of corresponding amplitudes.
              'image_path' (str): The path where the output image was saved.
    """
    # --- Internal logic using scipy.fft ---
    signal_data = data.get('signal_data')
    if signal_data is None:
        print("Warning: No signal data provided for create_fft_spectrum tool.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_fft_spectrum tool.")

    N = len(signal_data)
    if N == 0:
        # Handle empty signal case gracefully
        empty_freqs = np.array([])
        empty_amps = np.array([])
        # Create a blank plot
        plt.figure(figsize=(10, 6))
        plt.title('FFT Spectrum (Empty Input)')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude')
        plt.savefig(output_image_path)
        plt.close()
        return {
            'frequencies': empty_freqs,
            'amplitudes': empty_amps,
            'domain': 'frequency-spectrum',
            'image_path': output_image_path
        }

    # Calculate the frequency bins and the FFT
    yf = fft(signal_data)
    xf = fftfreq(N, 1 / sampling_rate)

    # --- Process for a one-sided amplitude spectrum ---
    # We only need the positive frequencies up to the Nyquist frequency
    positive_indices = np.where(xf >= 0)
    xf_positive = xf[positive_indices]
    
    # Normalize the amplitude. Multiply by 2/N for a correct amplitude scaling.
    # The DC component (at 0 Hz) is not multiplied by 2.
    yf_amplitude = np.abs(yf[positive_indices]) / N
    if N % 2 == 0: # Even number of samples
        yf_amplitude[1:len(yf_amplitude)-1] = yf_amplitude[1:len(yf_amplitude)-1] * 2
    else: # Odd number of samples
        yf_amplitude[1:] = yf_amplitude[1:] * 2

    # --- Generate and save the visual output ---
    plt.figure(figsize=(10, 8))
    plt.plot(xf_positive, yf_amplitude)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title('FFT Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude')
    plt.xlim([0, sampling_rate / 2]) # Explicitly set x-axis to Nyquist
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()

    # --- Return the structured data output ---
    results = {
        'frequencies': xf_positive,
        'amplitudes': yf_amplitude,
        'domain': 'frequency-spectrum',
        'primary_data': 'amplitudes',
        'secondary_data': 'frequencies',
        'image_path': output_image_path
    }

    return results

