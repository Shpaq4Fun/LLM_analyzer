# **Tool: lowpass\_filter**

## **1\. Purpose**

Attenuates or removes high-frequency components from a signal above a specified cutoff frequency.

## **2\. Strategic Advice**

This is a versatile tool with several distinct applications based on the chosen cutoff\_freq.

1. **Denoising:** The most common use. If high-frequency content is known to be noise, applying a low-pass filter can clean the signal for clearer visualization or more accurate feature calculation.  
2. **Component Isolation:** When a signal contains multiple components at different frequency bands (as seen on a spectrogram), this filter can isolate a specific low-frequency component of interest for individual analysis.  
3. **Anti-Aliasing before Downsampling:** This is a mandatory procedural step. Before reducing a signal's sampling rate, a low-pass filter must be applied with a cutoff\_freq below the target Nyquist frequency (new sampling rate / 2\) to prevent signal distortion.  
4. **Envelope Smoothing:** When applied to a signal's envelope (the output of a Hilbert transform), a gentle low-pass filter can smooth out noisy ripples to produce a cleaner feature that better represents the true amplitude modulation.  
5. **Trend Extraction:** Using a very low cutoff\_freq (e.g., \< 1 Hz) effectively turns the filter into a baseline extractor. The output represents the slow-moving trend of the signal, which can then be subtracted from the original to detrend it.

## **3\. Input Specification**

* **Data Structure:** 1D NumPy array.  
* **Domain:** Time-series signal or a 1D time-domain feature (e.g., a signal envelope).

## **4\. Output Specification**

* **Data Structure:** 1D NumPy array of the same length as the input.  
* **Domain / Context:** The same as the input, but with high-frequency components attenuated.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | np.ndarray | Input data dictionary containing the signal\_data and sampling\_rate. | Yes | None |
| output\_image\_path | str | The full path to save the output PNG to. | Yes | None |
| cutoff\_freq | float | The filter cutoff frequency in Hz. | Yes | None |
| order | int | The order of the filter. Higher orders have a sharper rolloff. | No | 4 |

## **6\. Next Steps Enabled**

* Applying FFT or Spectrogram to the filtered signal to see the effect of the filtering.  
* Using the denoised signal as input for more sensitive tools.  
* Downsampling the anti-aliased signal.  
* Calculating features on the smoothed envelope.  
* Subtracting the extracted trend from the original signal.

## **7\. Example Usage**
```
# Action to denoise a signal by removing frequencies above 5000 Hz  
denoise_action = {  
    "tool_name": "lowpass_filter",  
    "params": {  
        "data": loaded_data,  
        "output_image_path": "./outputs/step_2_lowpass_filter.png"  
        "cutoff_freq": 5000  
    },  
    "output_variable": "denoised_signal"  
}

# The system's translator would convert this action to:  
# denoised_signal = tools.sigproc.lowpass_filter(...)  
```