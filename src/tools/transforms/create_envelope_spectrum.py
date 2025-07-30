import numpy as np
from scipy.signal import hilbert
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

def create_envelope_spectrum(
    data: dict,
    output_image_path: str
) -> dict:
    """
    Calculates and saves the Envelope Spectrum of a signal.

    This process involves applying a Hilbert transform to get the analytic signal,
    calculating the envelope (magnitude), and then performing an FFT on the
    mean-subtracted envelope to identify modulating frequencies.

    Args:
        data (dict): dictionary with data from previous step, with keys 
            'signal_data', 'sampling_rate' and 'output_image_path'.
        output_image_path (str): The full path where the output PNG image will be saved.

    Returns:
        dict: A dictionary containing the results, with the following keys:
              'frequencies' (np.ndarray): Array of modulating frequencies in Hz.
              'amplitudes' (np.ndarray): Array of corresponding envelope amplitudes.
              'image_path' (str): The path where the output image was saved.
    """
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for create_envelope_spectrum tool.")

    signal_data = data.get(primary_data)
    if signal_data is None:
        print("Warning: No signal data provided for create_envelope_spectrum tool.")

    sampling_rate = data.get('sampling_rate')
    if sampling_rate is None:
        print("Warning: No sampling rate provided for create_envelope_spectrum tool.")

    N = len(signal_data)
    if N == 0:
        # Handle empty signal case gracefully
        empty_freqs = np.array([])
        empty_amps = np.array([])
        plt.figure(figsize=(10, 6))
        plt.title('Envelope Spectrum (Empty Input)')
        plt.xlabel('Modulating Frequency [Hz]')
        plt.ylabel('Amplitude')
        plt.savefig(output_image_path)
        plt.close()
        return {
            'frequencies': empty_freqs,
            'amplitudes': empty_amps,
            'domain': 'frequency-spectrum',
            'primary_data': 'amplitudes',
            'secondary_data': 'frequencies',
            'sampling_rate': sampling_rate,
            'image_path': output_image_path
        }
    if len(signal_data.shape) == 1:
        # --- Step 1: Calculate the envelope using the Hilbert transform ---
        # The analytic signal contains the original signal and its Hilbert transform
        analytic_signal = hilbert(signal_data)
        # The envelope is the absolute value (magnitude) of the analytic signal
        envelope = np.abs(analytic_signal)
        # Subtract the mean to remove the DC component before FFT
        envelope_no_dc = envelope - np.mean(envelope)
        
        # --- Step 2: Calculate the FFT of the envelope ---
        yf = fft(envelope_no_dc)
        xf = fftfreq(N, 1 / sampling_rate)

        # Process for a one-sided amplitude spectrum
        positive_indices = np.where(xf >= 0)
        xf_positive = xf[positive_indices]
        
        # Normalize the amplitude
        yf_amplitude = np.abs(yf[positive_indices]) / N
        if N % 2 == 0:
            yf_amplitude[1:len(yf_amplitude)-1] *= 2
        else:
            yf_amplitude[1:] *= 2

        # --- Generate and save the visual output ---
        plt.figure(figsize=(10, 8))
        plt.plot(xf_positive, yf_amplitude)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.title('Envelope Spectrum')
        plt.xlabel('Modulating Frequency [Hz]')
        plt.ylabel('Amplitude')
        # Envelope spectra are typically viewed at lower frequencies
        # We can set a sensible default x-limit or make it a parameter later
        plt.xlim([0, min(300, sampling_rate / 2)])
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
            'sampling_rate': sampling_rate,
            'image_path': output_image_path
        }
    elif signal_data.shape[1] >1:
        secondary_data = data.get('secondary_data')
        if secondary_data is None:
            print("Warning: No primary data provided for create_envelope_spectrum tool.")

        xf_positive = data.get(secondary_data)
        if xf_positive is None:
            print("Warning: No cyclic_frequencies data provided for create_envelope_spectrum tool.")

        yf_amplitude = np.sum(signal_data, axis=0)

        # --- Generate and save the visual output ---
        plt.figure(figsize=(10, 8))
        plt.plot(xf_positive, yf_amplitude)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.title('Enhanced Envelope Spectrum')
        plt.xlabel('Modulating Frequency [Hz]')
        plt.ylabel('Amplitude')
        # Envelope spectra are typically viewed at lower frequencies
        # We can set a sensible default x-limit or make it a parameter later
        # plt.xlim([0, min(300, sampling_rate / 2)])
        plt.tight_layout()
        plt.savefig(output_image_path)
        plt.close()

        results = {
            'frequencies': xf_positive,
            'amplitudes': yf_amplitude,
            'domain': 'frequency-spectrum',
            'primary_data': 'amplitudes',
            'secondary_data': 'frequencies',
            'sampling_rate': sampling_rate,
            'image_path': output_image_path
        }
    return results
