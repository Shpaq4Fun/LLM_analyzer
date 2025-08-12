# **Tool: create\_envelope\_spectrum**

## **1\. Purpose**

Identifies the repetition frequencies of amplitude modulations within a signal, which are often not visible in a standard FFT spectrum.

## **2\. Strategic Advice**

This is the primary tool for diagnosing faults that generate periodic impacts, such as bearing defects, gear tooth cracks, or reciprocating machinery issues. The key idea is to first isolate a high-frequency carrier band where the impacts excite resonance (e.g., using a bandpass filter based on a spectrogram's analysis) and then apply this tool to the filtered signal. The peaks in the resulting envelope spectrum will correspond to the actual fault repetition rates (modulating frequencies), not the high carrier frequencies.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 1D time-series signal array (or a 2D matrix for enhanced spectrum).
  * `sampling_rate`: The sampling rate of the signal in Hz.
  * `secondary_data` (for matrix input): The name of the key for the x-axis array.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the envelope spectrum and its metadata.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `frequencies`: 1D NumPy array of the modulating frequencies (Hz).
  * `amplitudes`: 1D NumPy array of the corresponding amplitudes.
  * `domain`: A string identifier, set to 'frequency-spectrum'.
  * `primary_data`: Set to 'amplitudes'.
  * `secondary_data`: Set to 'frequencies'.
  * `sampling_rate`: The original sampling rate.
  * `image_path`: The file path to the saved plot of the spectrum.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the signal data and sampling rate. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |

## **6\. Next Steps Enabled**

* **Fault Diagnosis:** The primary next step is to perform peak detection on the output spectrum and compare the identified modulating frequencies against known characteristic fault frequencies of the machinery (e.g., BPFI, BPFO for a bearing).
* **Harmonic Analysis:** Identifying families of harmonics in the envelope spectrum can confirm a diagnosis and indicate the severity of the fault.

## **7\. Example Usage**
```
# Assuming 'bandpassed_signal' is the output from a previous filtering step
envelope_action = {
    "tool_name": "create_envelope_spectrum",
    "params": {
        "data": bandpassed_signal,
        "output_dir": "./outputs/run_xyz/"
    },
    "output_variable": "envelope_results"
}

# The system's translator would convert this action to:
# envelope_results = tools.transforms.create_envelope_spectrum(...)
```
