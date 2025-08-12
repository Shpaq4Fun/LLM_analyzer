import numpy as np
from scipy.signal import hilbert
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import os, pickle
def create_envelope_spectrum(
    data: dict,
    output_image_path: str
) -> dict:
    """
    Calculate and save the envelope spectrum of a signal.

    Steps:
    - Hilbert transform -> analytic signal -> magnitude (envelope)
    - Remove DC (mean)
    - FFT of the envelope and keep one-sided spectrum

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the array key holding the input signal (1D) or matrix
    - sampling_rate: int, sampling frequency in Hz
    - secondary_data: str, optional, for enhanced spectrum case

    Returns:
    - dict with keys:
        frequencies, amplitudes, domain ('frequency-spectrum'), primary_data,
        secondary_data, sampling_rate, image_path
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
        plt.figure(figsize=(8, 6))
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

        if not os.path.isfile(output_image_path):
            # --- Generate and save the visual output ---
            fig, ax = plt.subplots(1,1,figsize=(7, 6))
            ax.plot(xf_positive, yf_amplitude)
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.set_title('Envelope Spectrum')
            ax.set_xlabel('Modulating Frequency [Hz]')
            ax.set_ylabel('Amplitude')
            # Envelope spectra are typically viewed at lower frequencies
            # We can set a sensible default x-limit or make it a parameter later
            ax.set_xlim([0, min(300, sampling_rate / 2)])
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

        if not os.path.isfile(output_image_path):
            # --- Generate and save the visual output ---
            fig, ax = plt.subplots(1,1,figsize=(7, 6))
            ax.plot(xf_positive, yf_amplitude)
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.set_title('Enhanced Envelope Spectrum')
            ax.set_xlabel('Modulating Frequency [Hz]')
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
