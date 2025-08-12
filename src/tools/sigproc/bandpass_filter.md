# **Tool: bandpass\_filter**

## **1\. Purpose**

Isolates a specific frequency band from a signal, attenuating frequencies both below the lower cutoff and above the upper cutoff.

## **2\. Strategic Advice**

This is a highly targeted tool used to "zoom in" on a specific frequency range of interest. Its application is almost always informed by a previous analysis step.

1. **Component Isolation:** Its primary purpose. After a wideband analysis tool (like create\_signal\_spectrogram or a cyclostationary map) identifies a "hotspot" or carrier band containing important activity, this filter is used to cut out that specific band for detailed analysis, significantly improving the signal-to-noise ratio.
2. **Prerequisite for Envelope Analysis:** This is a crucial procedural step for fault diagnosis. To accurately detect modulating frequencies (e.g., fault repetition rates), the signal **must** first be bandpass filtered around a resonant band where impacts are visible. Applying create\_envelope\_spectrum to the output of this tool is a standard and powerful diagnostic workflow.
3. **Harmonic/Sideband Inspection:** Can be used to isolate a single carrier frequency and its immediate sidebands, removing interference from other components to allow for a precise analysis of a specific modulation effect.

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
| lowcut\_freq | float | The lower cutoff frequency in Hz. | Yes | None |
| highcut\_freq | float | The upper cutoff frequency in Hz. | Yes | None |
| order | int | The order of the filter. Higher orders have a sharper rolloff. | No | 4 |

## **6\. Next Steps Enabled**

* Applying create\_envelope\_spectrum to the filtered signal to identify modulating frequencies (the most common next step).
* Applying create\_fft\_spectrum to the output to confirm that only the desired frequency band remains.
* Calculating statistical features (like kurtosis) on the filtered signal to quantify its impulsiveness.

## **7\. Example Usage**
```
# Action to isolate the frequency band between 2000 Hz and 4000 Hz
bandpass_action = {
    "tool_name": "bandpass_filter",
    "params": {
        "data": loaded_data,
        "output_dir": "./outputs/run_xyz/",
        "lowcut_freq": 2000,
        "highcut_freq": 4000
    },
    "output_variable": "bandpassed_signal"
}

# The system's translator would convert this action to:
# bandpassed_signal = tools.sigproc.bandpass_filter(...)
```
