# **Tool: create\_envelope\_spectrum**

## **1\. Purpose**

Identifies the repetition frequencies of amplitude modulations within a signal, which are often not visible in a standard FFT spectrum.

## **2\. Strategic Advice**

This is the primary tool for diagnosing faults that generate periodic impacts, such as bearing defects, gear tooth cracks, or reciprocating machinery issues. The key idea is to first isolate a high-frequency carrier band where the impacts excite resonance (e.g., using a bandpass filter based on a spectrogram's analysis) and then apply this tool to the filtered signal. The peaks in the resulting envelope spectrum will correspond to the actual fault repetition rates (modulating frequencies), not the high carrier frequencies.

## **3\. Input Specification**

* **Data Structure:** 1D NumPy array.  
* **Domain:** Time-series signal. Critically, this signal should ideally be **bandpass-filtered** around a resonant frequency band identified in a previous step. Applying it to a raw, wideband signal is less effective.

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing three keys.  
* **Domain / Context:**  
  * frequencies: 1D NumPy array of the **modulating frequencies** in Hertz (Hz).  
  * amplitudes: 1D NumPy array of the corresponding amplitudes of the envelope's frequency components.  
  * image\_path: A string path to the saved PNG visualization of the envelope spectrum.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| signal\_data | np.ndarray | 1D NumPy array of the (ideally filtered) time-domain signal. | Yes | None |
| sampling\_rate | int | The sampling frequency (in Hz) of the signal\_data provided. | Yes | None |
| output\_image\_path | str | The full path to save the output PNG to. | Yes | None |

## **6\. Next Steps Enabled**

* **Fault Diagnosis:** The primary next step is to perform peak detection on the output spectrum and compare the identified modulating frequencies against known characteristic fault frequencies of the machinery (e.g., BPFI, BPFO for a bearing).  
* **Harmonic Analysis:** Identifying families of harmonics in the envelope spectrum can confirm a diagnosis and indicate the severity of the fault.

## **7\. Example Usage**
```
# Assuming 'bandpassed_signal' is a 1D NumPy array from a previous filtering step  
envelope_action = {  
    "tool_name": "create_envelope_spectrum",  
    "params": {  
        "signal_data": bandpassed_signal,  
        "sampling_rate": 50000,  
        "output_image_path": "./outputs/step_2_envelope_spectrum.png"  
    },  
    "output_variable": "envelope_results"  
}

# The system's translator would convert this action to:  
# envelope_results = tools.transforms.create_envelope_spectrum(...)
