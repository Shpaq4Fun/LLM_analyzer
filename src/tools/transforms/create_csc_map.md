# **Tool: create\_csc\_map**

## **1\. Purpose**

Calculates the Cyclic Spectral Coherence (CSC) to reveal hidden periodicities in a signal by identifying correlations between different frequency components.

## **2\. Strategic Advice**

This is an advanced and computationally intensive analysis tool that is exceptionally powerful for detecting cyclostationary signals buried in heavy noise. **Use this tool when a standard spectrogram fails to show clear impulsive features but a fault is still suspected.**

The CSC map is a bi-frequency representation that directly links **modulating frequencies (the alpha axis)** to the **carrier frequencies (the f axis)** they affect. A strong peak at a coordinate (alpha, f) is conclusive evidence that a cyclic event with frequency alpha is modulating the signal content at frequency f. This makes it superior to the spectrogram-then-envelope workflow for low signal-to-noise ratio cases, as it performs the demodulation and frequency analysis in a single, more robust step. If the investigaiton is focused at some candidate modulation frequency, it is important to set the `max_alpha` parameter at at least four times that frequency to be able to observe at least four harmonic components.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 1D time-series signal array.
  * `sampling_rate`: The sampling rate of the signal in Hz.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the CSC map and its metadata.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `cyclic_frequencies`: 1D NumPy array of the cyclic frequencies (alpha axis).
  * `carrier_frequencies`: 1D NumPy array of the carrier frequencies (f axis).
  * `csc_map`: The 2D NumPy array representing the coherence magnitude.
  * `domain`: A string identifier, set to 'bi-frequency-matrix'.
  * `primary_data`: Set to 'csc_map'.
  * `secondary_data`: Set to 'cyclic_frequencies'.
  * `tertiary_data`: Set to 'carrier_frequencies'.
  * `sampling_rate`: The original sampling rate.
  * `original_signal_data`: The original input signal.
  * `image_path`: The file path to the saved plot of the map.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the signal data and sampling rate. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |
| min\_alpha | int | The minimum cyclic frequency (alpha) to calculate, in Hz. | No | 1 |
| max\_alpha | int | The maximum cyclic frequency (alpha) to calculate, in Hz. | No | 150 |
| window | int | The length of each segment for analysis (nfft). | No | 256 |
| overlap | int | Number of overlapping points between segments. | No | 220 |

## **6\. Next Steps Enabled**

* **Direct Fault Diagnosis:** The primary next step is to perform 2D peak detection on the csc\_map. The coordinates of the most prominent peak directly provide the fault's modulating frequency (alpha) and the carrier frequency band (f) it excites.
* **Quantitative Selector Analysis:** The csc\_map output is further passed to the **Quantitative Parameterization Module** to calculate diagnostic selectors and selector-based enhanced envelope spectra. For example, a "Cyclic Frequency Kurtosis" selector is computed by measuring kurtosis along the carrier frequency axis for each cyclic frequency. The peaks in this selector automatically highlight the most impulsive and interesting alpha frequencies.
* **Enhanced Envelope Spectrum Calculation:** This is a powerful technique. By using a selector to identify the optimal carrier frequency band, the csc\_map can be integrated along that band of the f axis. This produces an **enhanced envelope spectrum**—a 1D plot vs. alpha—that is far cleaner and more selective than one derived from a standard spectrogram.
* **Targeted Filtering:** The identified carrier frequency f can be used to design a highly precise bandpass filter to isolate the fault signature from the original time-series signal.
* **Decomposition:** The csc\_map can be used as input for nonnegative matrix decomposition (NMF) to separate and analyze individual fault components.

## **7\. Example Usage**
```
# Action to perform advanced cyclostationary analysis with custom parameters
csc_action = {
    "tool_name": "create_csc_map",
    "params": {
        "data": loaded_data,
        "output_dir": "./outputs/run_xyz/",
        "max_alpha": 300,
        "window": 512
    },
    "output_variable": "csc_results"
}

# The system's translator would convert this action to:
# csc_results = tools.transforms.create_csc_map(...)
```
