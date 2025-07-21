# **Tool: create\_signal\_spectrogram**

## **1\. Purpose**

Calculates and visualizes the spectrogram of a time-series signal, showing its frequency content over time.

## **2\. Strategic Advice**

This tool is a fundamental first step for analyzing any time-varying or non-stationary signal, especially in domains like vibration analysis, audio processing, bio-signals or other signals sampled at high sampling frequencies (above 1000 Hz). Its primary use is to visually identify how the spectral characteristics of a signal evolve. For bearing fault diagnosis, look for periodic vertical stripes (impulsive components) which indicate a fault signature. The frequency range of these stripes is a critical piece of information for subsequent analysis.

## **3\. Input Specification**

* **Data Structure:** 1D NumPy array.  
* **Domain:** Time-series signal.

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing four keys.  
* **Domain / Context:**  
  * frequencies: 1D NumPy array of the frequency bins.  
  * times: 1D NumPy array of the time steps.  
  * Sxx\_db: A 2D NumPy array (frequencies x times) representing the signal's power in decibels (dB) at each point in the time-frequency plane.  
  * image\_path: A string path to the saved PNG visualization.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | np.ndarray | Input data dictionary containing the signal\_data and sampling\_rate. | Yes | None |
| output\_image\_path | str | The full path to save the output PNG to. | Yes | None |
| nperseg | int | The length of each segment. A larger value increases frequency resolution but decreases time resolution. | No | 256 |
| noverlap | int | Number of overlapping points between segments. Usually set to 50% of nperseg. | No | 128 |

## **6\. Next Steps Enabled**

* Visual analysis to identify constant frequency components (harmonics) or time-localized events (impulses).  
* Identification of a **carrier frequency band** for a specific signal component (e.g., a bearing fault signature).  
* Provides a 2D matrix (Sxx\_db) that can be used as:
	* Direct input for **matrix decomposition tools** (like NMF) to separate signal sources;
	* Basis vor visual analysis aiming for estimating carrier frequency bands that given signal components occupy. This information can lead to designing targeted filters that aim to extract individual components from the signal.

## **7\. Example Usage**
```
# Assuming 'my_signal' is a 1D NumPy array and 'fs' is the sampling rate  
spectrogram_action = {  
    "tool_name": "create_signal_spectrogram",  
    "params": {  
        "signal_data": my_signal,  
        "sampling_rate": fs,  
        "output_image_path": "./outputs/step_2_spectrogram.png",  
        "nperseg": 512  
    },  
    "output_variable": "spectrogram_results"  
}

# The system's translator would convert this action to:  
# spectrogram_results = tools.transforms.create_signal_spectrogram(...)  
```
