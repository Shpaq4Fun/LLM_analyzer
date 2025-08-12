"""
Quantitative parameterization of tool outputs.

- Dispatcher calculate_quantitative_metrics adds domain-specific metrics to tool outputs
- Supports time-series, frequency spectra, time-frequency matrices, cyclostationary maps,
  and NMF decompositions
- Also produces and persists supplementary figures for selectors where applicable
"""

# --- quantitative_parameterization_module.py ---

# Import necessary libraries
import numpy as np
from scipy.stats import kurtosis, skew, levy_stable, jarque_bera
from scipy.signal import find_peaks, istft, firwin2, stft, filtfilt
import os, pickle
import matplotlib.pyplot as plt

# === Helper Functions ===

def _extract_ids_from_path(image_path: str) -> tuple:
    """
    Extracts run_id and action_id from a formatted image path string.
    e.g., './run_state/run_20250716_125140/step1_fft_spectrum.png'
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

def calculate_gini_index(array):
    """Calculate the Gini coefficient of a numpy array."""
    array = array.flatten()
    if np.amin(array) < 0:
        array -= np.amin(array)
    array += 0.0000001
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

def estimate_alpha_stable(array):
    """Placeholder for a more complex alpha estimation."""
    array = array.flatten()
    return 2-levy_stable._fitstart(array)[0]

def normalize_data(data):
    return (data-np.min(data))/(np.max(data)-np.min(data))

# === The Dispatcher Function (Public) ===

def calculate_quantitative_metrics(tool_output: dict) -> dict:
    """
    Takes the full dictionary output from a tool, dispatches it to the
    correct handler, and returns the dictionary *updated* with new metrics.
    """
    if not tool_output or not isinstance(tool_output, dict):
        return {}

    domain = tool_output.get('domain', 'unknown_domain')
    print(domain)
    if domain == 'time-series':
        new_params = _calculate_timeseries_stats(tool_output)
    elif domain == 'time-frequency-matrix':
        new_params = _calculate_spectrogram_stats(tool_output)
    elif domain == 'frequency-spectrum':
        new_params = _calculate_spectrum_stats(tool_output)
    elif domain == 'bi-frequency-matrix':
        new_params = _calculate_cyclomap_stats(tool_output)
    elif domain == 'decomposed_matrix':
        new_params = _calculate_nmf_stats(tool_output)
    else:
        new_params = {}
    tool_output["new_params"] = new_params
    return tool_output

# === Specialized Handler Functions (Private) ===

def _calculate_timeseries_stats(data_dict: dict) -> dict:
    """
    Calculates key statistical moments for a 1D time-series signal
    and merges them into the input dictionary.
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

def _calculate_spectrum_stats(data_dict: dict) -> dict:
    """
    Calculates metrics for a 1D frequency spectrum and merges them
    into the input dictionary.
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

def _calculate_spectrogram_stats(data_dict: dict) -> dict:
    """
    Calculates key stats AND a suite of diagnostic selectors for a 2D spectrogram.
    """
    image_path = data_dict.get('image_path')
    # Handle the case where image_path is a list
    primary_image_path = image_path[0] if isinstance(image_path, list) else image_path
    run_id, action_id = _extract_ids_from_path(primary_image_path)

    if run_id is None or action_id is None:
        return data_dict

    primary_data_key = data_dict.get('primary_data')
    spectrogram_matrix = data_dict.get(primary_data_key)
    tertiary_data_key = data_dict.get('tertiary_data')
    frequencies = data_dict.get(tertiary_data_key)

    if spectrogram_matrix is None or frequencies is None or spectrogram_matrix.size == 0:
        return data_dict

    gini = calculate_gini_index(spectrogram_matrix.flatten())

    num_freq_bins = spectrogram_matrix.shape[0]
    sk_selector = np.zeros(num_freq_bins)
    jb_selector = np.zeros(num_freq_bins)
    alpha_selector = np.zeros(num_freq_bins)
    joint_selector = np.zeros(num_freq_bins)
    for i in range(num_freq_bins):
        energy_slice = spectrogram_matrix[i, :]
        sk_selector[i] = kurtosis(energy_slice, fisher=False)
        jb_selector[i] = jarque_bera(energy_slice)[0]
        alpha_selector[i] = estimate_alpha_stable(energy_slice)
        joint_selector[i] = sk_selector[i] * jb_selector[i] * alpha_selector[i]

    sk_selector = normalize_data(sk_selector)
    jb_selector = normalize_data(jb_selector)
    alpha_selector = normalize_data(alpha_selector)
    joint_selector = normalize_data(joint_selector)

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
    ax2.set_ylabel('Joint Parameter', color=color)
    ax1.plot(frequencies, joint_selector, color=color, linestyle='-', label='Joint Selector', linewidth=3)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 1)

    fig.suptitle('Diagnostic Selectors')
    fig.tight_layout()
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.savefig(selectors_image_path)
    fig_path = os.path.join(f"{selectors_image_path[:-2]}kl")
    with open(fig_path, 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

    peak_sk_freq_hz = frequencies[np.argmax(sk_selector)]
    peak_jb_freq_hz = frequencies[np.argmax(jb_selector)]
    peak_alpha_freq_hz = frequencies[np.argmin(alpha_selector)]

    new_params = {
        "sparsity_gini_index": float(gini),
        "peak_kurtosis_freq_hz": float(peak_sk_freq_hz),
        "peak_jarque_bera_freq_hz": float(peak_jb_freq_hz),
        "min_alpha_freq_hz": float(peak_alpha_freq_hz),
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

def _calculate_cyclomap_stats(data_dict: dict) -> dict:
    """
    Calculates key stats AND a suite of diagnostic selectors for a 2D spectrogram.
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

    num_freq_bins = csc_map.shape[0]
    sk_selector = np.zeros(num_freq_bins)
    jb_selector = np.zeros(num_freq_bins)
    alpha_selector = np.zeros(num_freq_bins)
    joint_selector = np.zeros(num_freq_bins)
    for i in range(num_freq_bins):
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
        ax1.set_ylim(0, 1)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linewidth=0.5)

        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Joint Parameter', color=color)
        ax2.plot(carrier_frequencies, joint_selector, color=color, linestyle='-', label='Joint Parameter', linewidth=3)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1)

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

    peak_sk_freq_hz = carrier_frequencies[np.argmax(sk_selector)]
    peak_jb_freq_hz = carrier_frequencies[np.argmax(jb_selector)]
    peak_alpha_freq_hz = carrier_frequencies[np.argmin(alpha_selector)]


    num_alpha_bins = csc_map.shape[1]
    sk_ies = np.zeros(num_alpha_bins)
    jb_ies = np.zeros(num_alpha_bins)
    alpha_ies = np.zeros(num_alpha_bins)
    joint_ies = np.zeros(num_alpha_bins)
    for i in range(num_alpha_bins):
        alpha_slice = csc_map[:,i]
        sk_ies[i] = sum(np.multiply(alpha_slice,sk_selector))
        jb_ies[i] = sum(np.multiply(alpha_slice,jb_selector))
        alpha_ies[i] = sum(np.multiply(alpha_slice,alpha_selector))
        joint_ies[i] = sum(np.multiply(alpha_slice,joint_selector))

    ees_image_path = os.path.join(f"./run_state/{run_id}", f"step_{action_id}_PIES.png")
    if not os.path.isfile(ees_image_path):
        fig, ax1 = plt.subplots(figsize=(12, 8))

        color = 'tab:blue'
        ax1.set_xlabel('Modulating Frequency [Hz]')
        ax1.set_ylabel('Value', color=color)
        ax1.plot(cyclic_frequencies, sk_ies, color=color, linestyle='-', label='Spectral Kurtosis')
        ax1.plot(cyclic_frequencies, jb_ies, color=color, linestyle='--', label='Jarque-Bera')
        ax1.plot(cyclic_frequencies, alpha_ies, color=color, linestyle=':', label='Alpha Parameter')

        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, which='both', linewidth=0.5)

        color = 'tab:red'
        ax2 = ax1.twinx()
        ax2.set_ylabel('Joint Parameter', color=color)
        ax2.plot(cyclic_frequencies, joint_ies, color=color, linestyle='-', label='Joint Parameter', linewidth=3)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1)

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
        "peak_kurtosis_freq_hz": float(peak_sk_freq_hz),
        "peak_jarque_bera_freq_hz": float(peak_jb_freq_hz),
        "min_alpha_freq_hz": float(peak_alpha_freq_hz),
        # "selectors_data": {
        #     "frequencies_hz": carrier_frequencies.tolist(),
        #     "spectral_kurtosis": sk_selector.tolist(),
        #     "jarque_bera": jb_selector.tolist(),
        #     "alpha_stable": alpha_selector.tolist(),
        #     "cyclic_frequencies_hz": cyclic_frequencies.tolist(),
        #     "sk_ies": sk_ies.tolist(),
        #     "jb_ies": jb_ies.tolist(),
        #     "alpha_ies": alpha_ies.tolist()
        # },
        "supporting_image_paths": {
            "selectors_image_path": selectors_image_path,
            "ees_image_path": ees_image_path
        }
    }

    # data_dict.update(new_params)
    return new_params

def _calculate_nmf_stats(data_dict: dict) -> dict:
    """
    Calculates key stats AND a suite of diagnostic selectors for a 2D spectrogram.
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
    n_iter = 32
    signals_reconstructed = []

    if domain == 'time-frequency-matrix':
        nperseg = data_dict.get('nperseg')
        noverlap = data_dict.get('noverlap')
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
                    nfft=2*nperseg
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
            W_comp = W[:, i]

            # --- 1. Design the Custom FIR Filter ---
            # The W_component is our desired gain at each frequency. We normalize it to be between 0 and 1.
            normalized_gain = (W_comp - np.min(W_comp)) / (np.max(W_comp) - np.min(W_comp) + 1e-9)

            # firwin2 requires frequencies to be normalized to the Nyquist frequency.
            nyquist = sampling_rate / 2.0
            normalized_freqs = carrier_frequencies / nyquist

            # Ensure frequencies start at 0 and end at 1 (for Nyquist)
            # freqs = np.concatenate(([0], normalized_freqs, [1]))
            # gains = np.concatenate(([0], normalized_gain, [0]))
            freqs = normalized_freqs
            gains = normalized_gain
            # Design the filter
            # The filter order must be even for firwin2
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
        ax[i].plot(time_axis, signals_reconstructed[i])
        ax[i].set_title(f'Reconstructed Component {i+1}')
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
