# **Tool: create\_fft\_spectrum**

## **1\. Purpose**

Calculates the Fast Fourier Transform (FFT) of a time-series signal to show its overall frequency content.

## **2\. Strategic Advice**

This tool is used to analyze the **stationary** or **time-averaged** frequency composition of a signal. Unlike a spectrogram, which shows how frequencies evolve over time, the FFT provides a single view of which frequencies are dominant across the entire signal duration. It is excellent for identifying stable, persistent frequency components like shaft rotational speed, its harmonics, or carrier frequencies of other modulations.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 1D time-series signal array.
  * `sampling_rate`: The sampling rate of the signal in Hz.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the FFT spectrum and its metadata.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `frequencies`: 1D NumPy array of the frequency bins (Hz).
  * `amplitudes`: 1D NumPy array of the corresponding amplitudes (one-sided, scaled).
  * `domain`: A string identifier, set to 'frequency-spectrum'.
  * `primary_data`: Set to 'amplitudes'.
  * `secondary_data`: Set to 'frequencies'.
  * `image_path`: The file path to the saved plot of the spectrum.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the signal data and sampling rate. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |

## **6\. Next Steps Enabled**

* **Peak Detection:** The frequencies and amplitudes arrays can be passed to a peak detection tool to automatically find and list the most dominant frequencies.
* **Filter Validation:** Can be used to visualize the signal's frequency content before and after applying a filter to confirm the filter worked as intended.
* **Harmonic Analysis:** Helps identify families of related peaks (harmonics) that can point to a specific mechanical or electrical source.

## **7\. Example Usage**
```
# Assuming 'loaded_data' is the output from a previous step
fft_action = {
    "tool_name": "create_fft_spectrum",
    "params": {
        "data": loaded_data,
        "output_dir": "./outputs/run_xyz/"
    },
    "output_variable": "fft_results"
}

# The system's translator would convert this action to:
# fft_results = tools.transforms.create_fft_spectrum(...)
```
