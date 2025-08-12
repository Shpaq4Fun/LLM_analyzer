# **Tool: highpass\_filter**

## **1\. Purpose**

Attenuates or removes low-frequency components from a signal below a specified cutoff frequency.

## **2\. Strategic Advice**

This tool has several distinct applications, primarily focused on removing unwanted low-frequency content.

1. **Removing Low-Frequency Operational Noise:** This is a key use case in machine diagnostics. High-energy but diagnostically uninteresting components (e.g., related to shaft rotation at 1x frequency) often dominate the low-frequency spectrum. Filtering them out significantly improves the signal-to-noise ratio for detecting subtle, higher-frequency fault signatures.
2. **Detrending and DC Offset Removal:** Using a very low cutoff\_freq (e.g., 0.1 Hz to 1 Hz) is a standard and effective method to remove slow-moving trends or constant DC offsets from a signal. This is often a necessary preprocessing step before performing an FFT.
3. **Emphasizing Transients (Differentiation):** A first-order high-pass filter acts as a simple differentiator, which can be used to accentuate sharp changes, transients, or impulses within the signal, making them easier to detect in subsequent steps.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 1D time-series signal array.
  * `sampling_rate`: The sampling rate of the signal in Hz.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the filtered signal and its metadata.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `filtered_signal`: A 1D NumPy array of the same length as the input, containing the filtered signal.
  * `domain`: A string identifier, set to 'time-series'.
  * `primary_data`: The key for the main data array, set to 'filtered_signal'.
  * `sampling_rate`: The sampling rate of the signal.
  * `image_path`: The file path to the saved plot of the filtered signal.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the signal data and sampling rate. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |
| cutoff\_freq | float | The filter cutoff frequency in Hz. | Yes | None |
| order | int | The order of the filter. Higher orders have a sharper rolloff. | No | 4 |

## **6\. Next Steps Enabled**

* Applying FFT or Spectrogram to the filtered signal to analyze the remaining high-frequency content.
* Using the filtered signal as a cleaner input for decomposition tools (like NMF).
* Applying create\_envelope\_spectrum to the high-pass filtered signal if a fault is suspected in a high carrier frequency band.

## **7\. Example Usage**
```
# Action to remove strong operational components below 1000 Hz
noise_removal_action = {
    "tool_name": "highpass_filter",
    "params": {
        "data": loaded_data,
        "output_dir": "./outputs/run_xyz/",
        "cutoff_freq": 1000
    },
    "output_variable": "high_freq_signal"
}

# The system's translator would convert this action to:
# high_freq_signal = tools.sigproc.highpass_filter(...)
```
