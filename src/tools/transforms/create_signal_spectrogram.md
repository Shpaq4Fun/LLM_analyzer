# **Tool: create\_signal\_spectrogram**

## **1\. Purpose**

Calculates and visualizes the spectrogram of a time-series signal, showing its frequency content over time.

## **2\. Strategic Advice**

This tool is a fundamental first step for analyzing any time-varying or non-stationary signal, especially in domains like vibration analysis, audio processing, bio-signals or other signals sampled at high sampling frequencies (above 1000 Hz). Its primary use is to visually identify how the spectral characteristics of a signal evolve. For bearing fault diagnosis, look for periodic vertical stripes (impulsive components) which indicate a fault signature. The frequency range of these stripes is a critical piece of information for subsequent analysis.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 1D time-series signal array.
  * `sampling_rate`: The sampling rate of the signal in Hz.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the spectrogram and its metadata.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `frequencies`: 1D NumPy array of the frequency bins.
  * `times`: 1D NumPy array of the time steps.
  * `Sxx_db`: The 2D NumPy array (power, not in dB) for downstream use. The plot is rendered in dB.
  * `domain`: A string identifier, set to 'time-frequency-matrix'.
  * `primary_data`: Set to 'Sxx_db'.
  * `secondary_data`: Set to 'times'.
  * `tertiary_data`: Set to 'frequencies'.
  * `sampling_rate`, `nperseg` (window), `noverlap`.
  * `original_phase`: The phase of the STFT.
  * `original_signal_data`: The original input signal.
  * `image_path`: The file path to the saved plot.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the signal data and sampling rate. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |
| window | int | The length of each segment (nperseg). | No | 1024 |
| noverlap | int | Number of overlapping points between segments. | No | 800 |

## **6\. Next Steps Enabled**

* Visual analysis to identify constant frequency components (harmonics) or time-localized events (impulses).
* Identification of a **carrier frequency band** for a specific signal component (e.g., a bearing fault signature).
* Provides a 2D matrix (Sxx\_db) that can be used as:
	* Direct input for **matrix decomposition tools** (like NMF) to separate signal sources;
	* Basis vor visual analysis aiming for estimating carrier frequency bands that given signal components occupy. This information can lead to designing targeted filters that aim to extract individual components from the signal.

## **7\. Example Usage**
```
# Assuming 'loaded_data' is the output from a previous step
spectrogram_action = {
    "tool_name": "create_signal_spectrogram",
    "params": {
        "data": loaded_data,
        "output_dir": "./outputs/run_xyz/",
        "window": 512
    },
    "output_variable": "spectrogram_results"
}

# The system's translator would convert this action to:
# spectrogram_results = tools.transforms.create_signal_spectrogram(...)
```
