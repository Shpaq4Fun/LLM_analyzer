import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import os, pickle
def create_fft_spectrum(
    data: dict,
    output_image_path: str
) -> dict:
    """
    Compute and save a one-sided FFT amplitude spectrum.

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the array key holding the input signal
    - sampling_rate: int, sampling frequency in Hz

    Returns:
    - dict with keys:
        frequencies, amplitudes, domain ('frequency-spectrum'), primary_data,
        secondary_data, image_path
    """
    # --- Internal logic using scipy.fft ---
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for create_envelope_spectrum tool.")

    signal_data = data.get(primary_data)
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

    if not os.path.isfile(output_image_path):
        # --- Generate and save the visual output ---
        fig, ax = plt.subplots(1,1,figsize=(7, 6))
        ax.plot(xf_positive, yf_amplitude)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title('FFT Spectrum')
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Amplitude')
        # Envelope spectra are typically viewed at lower frequencies
        # We can set a sensible default x-limit or make it a parameter later
        # ax.xlim([0, min(300, sampling_rate / 2)])
        plt.tight_layout()
        plt.savefig(output_image_path)
        fig_path = os.path.join(f"{output_image_path[:-2]}kl")
        with open(fig_path, 'wb') as f:
            pickle.dump(fig, f)
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

