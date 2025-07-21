# **Tool: create\_fft\_spectrum**

## **1\. Purpose**

Calculates the Fast Fourier Transform (FFT) of a time-series signal to show its overall frequency content.

## **2\. Strategic Advice**

This tool is used to analyze the **stationary** or **time-averaged** frequency composition of a signal. Unlike a spectrogram, which shows how frequencies evolve over time, the FFT provides a single view of which frequencies are dominant across the entire signal duration. It is excellent for identifying stable, persistent frequency components like shaft rotational speed, its harmonics, or carrier frequencies of other modulations.

## **3\. Input Specification**

* **Data Structure:** 1D NumPy array.  
* **Domain:** Time-series signal or a 1D time-domain feature.

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing three keys.  
* **Domain / Context:**  
  * frequencies: 1D NumPy array of the frequency bins in Hertz (Hz).  
  * amplitudes: 1D NumPy array of the corresponding signal amplitudes at each frequency.  
  * image\_path: A string path to the saved PNG visualization of the spectrum.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| signal\_data | np.ndarray | 1D NumPy array containing the time-domain signal or feature. | Yes | None |
| sampling\_rate | int | The sampling frequency (in Hz) of the signal\_data provided. | Yes | None |
| output\_image\_path | str | The full path to save the output PNG to. | Yes | None |

## **6\. Next Steps Enabled**

* **Peak Detection:** The frequencies and amplitudes arrays can be passed to a peak detection tool to automatically find and list the most dominant frequencies.  
* **Filter Validation:** Can be used to visualize the signal's frequency content before and after applying a filter to confirm the filter worked as intended.  
* **Harmonic Analysis:** Helps identify families of related peaks (harmonics) that can point to a specific mechanical or electrical source.

## **7\. Example Usage**
```
# Assuming 'filtered_feature' is a 1D NumPy array and 'feature_fs' is its sampling rate  
fft_action = {  
    "tool_name": "create_fft_spectrum",  
    "params": {  
        "signal_data": filtered_feature,   
        "output_image_path": "./outputs/step_2_fft_spectrum.png"  
    },  
    "output_variable": "fft_results"  
}

# The system's translator would convert this action to:  
# fft_results = tools.transforms.create_fft_spectrum(...)  
```