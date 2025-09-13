# Highpass Filter

<cite>
**Referenced Files in This Document**   
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L1-L63)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Purpose and Applications](#purpose-and-applications)
3. [Function Signature and Parameters](#function-signature-and-parameters)
4. [Implementation Details](#implementation-details)
5. [Zero-Phase Filtering Rationale](#zero-phase-filtering-rationale)
6. [Usage Examples in Fault Detection Workflows](#usage-examples-in-fault-detection-workflows)
7. [Common Pitfalls and Best Practices](#common-pitfalls-and-best-practices)
8. [Performance Tips for Large-Scale Signal Processing](#performance-tips-for-large-scale-signal-processing)

## Introduction
The `highpass_filter` tool is a critical preprocessing component in vibration signal analysis, designed to remove low-frequency noise, drift, or operational harmonics that can obscure diagnostic features. It leverages digital filtering techniques to preserve high-frequency transient events while attenuating unwanted low-frequency content. This document provides a comprehensive overview of its functionality, implementation, and best practices for use in fault detection systems.

**Section sources**
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L1-L10)

## Purpose and Applications
The highpass filter serves multiple strategic purposes in signal preprocessing:

1. **Removal of Low-Frequency Operational Noise**: In rotating machinery, strong spectral components at shaft rotational frequencies (1x, 2x, etc.) often dominate the low-frequency band. These components, while high in amplitude, are typically not indicative of incipient faults. By applying a highpass filter with a cutoff frequency above these harmonics, the signal-to-noise ratio for higher-frequency fault signatures (e.g., bearing defects, gear impacts) is significantly improved.

2. **Detrending and DC Offset Removal**: Slow drifts or constant offsets in sensor data can distort frequency domain analysis such as FFT. A highpass filter with a very low cutoff frequency (e.g., 0.1–1 Hz) effectively removes these trends without affecting the dynamic signal content, making it an essential step before spectral analysis.

3. **Transient Emphasis via Differentiation**: First-order highpass filters inherently act as differentiators, amplifying rapid changes in the signal. This property is useful for enhancing impulsive events like impacts or crack propagation, which are key indicators in early fault detection.

**Section sources**
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L11-L20)

## Function Signature and Parameters
The `highpass_filter` function implements a zero-phase Butterworth highpass filter and returns both the filtered signal and metadata.

```python
def highpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    cutoff_freq: float = 3500,
    order: int = 4
) -> Dict[str, Any]:
```

### Parameters
| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | Input dictionary containing signal data and sampling rate | Yes | None |
| output_image_path | str | File path where the filtered signal plot will be saved | Yes | None |
| cutoff_freq | float | Cutoff frequency in Hz; frequencies below this are attenuated | No | 3500 |
| order | int | Order of the Butterworth filter; controls roll-off steepness | No | 4 |

### Input Requirements
The `data` dictionary must contain:
- `primary_data`: string key pointing to the 1D NumPy array of the time-series signal.
- `sampling_rate`: integer or float representing the sampling frequency in Hz.

### Return Value
The function returns a dictionary with the following keys:
- `filtered_signal`: np.ndarray, the zero-phase filtered time-domain signal.
- `domain`: str, set to `'time-series'`.
- `primary_data`: str, set to `'filtered_signal'` for downstream compatibility.
- `sampling_rate`: float, original sampling rate.
- `image_path`: str, path to the generated plot.
- `filter_params`: dict, containing filter type, order, cutoff frequency, and normalized cutoff.

**Section sources**
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L6-L68)
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L21-L44)

## Implementation Details
The filter is implemented using `scipy.signal.butter` for design and `scipy.signal.filtfilt` for application.

### Filter Design
1. **Nyquist Frequency Calculation**: The Nyquist frequency is computed as half the sampling rate.
   ```python
   nyquist_freq = 0.5 * sampling_rate
   ```

2. **Cutoff Frequency Normalization**: The cutoff frequency is normalized relative to the Nyquist frequency (range [0, 1]) for compatibility with `scipy.signal.butter`.
   ```python
   cutoff_norm = cutoff_freq / nyquist_freq
   ```

3. **Butterworth Filter Coefficients**: The filter is designed using:
   ```python
   b, a = butter(N=order, Wn=cutoff_norm, btype='high', analog=False, output='ba')
   ```
   where `b` and `a` are the numerator and denominator coefficients of the filter transfer function.

### Input Validation
The function includes robust validation:
- Ensures `cutoff_freq > 0`
- Enforces `cutoff_freq < nyquist_freq` to prevent aliasing and signal loss
- Validates presence of required keys in input dictionary

### Zero-Phase Filtering
The filter is applied using `filtfilt`, which processes the signal in both forward and reverse directions:
```python
filtered_signal = filtfilt(b, a, signal_data, padlen=3*(max(len(a), len(b)) - 1))
```
This eliminates phase distortion and ensures no time shift in the output.

### Visualization
A plot of the filtered signal is saved to `output_image_path` using `matplotlib`. The plot includes:
- Time-domain waveform
- Grid, labels, and title with filter parameters
- Automatic directory creation if needed

**Section sources**
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L69-L152)

## Zero-Phase Filtering Rationale
Zero-phase filtering using `filtfilt` is essential in diagnostic applications because:
- **Preserves Transient Timing**: Unlike causal filters that introduce phase delay, `filtfilt` maintains the exact timing of impulses and transients, which is critical for detecting fault-related events.
- **Avoids Signal Distortion**: Phase shifts can smear transient events across time, reducing their amplitude and making them harder to detect.
- **Improves Diagnostic Accuracy**: Accurate temporal alignment ensures that features like impact periodicity or modulation sidebands are preserved in both time and frequency domains.

This approach is particularly valuable when analyzing signals for bearing faults, gear tooth damage, or other conditions where transient events are key indicators.

**Section sources**
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L95-L98)

## Usage Examples in Fault Detection Workflows
### Example 1: Removing Rotational Harmonics
```python
# Remove low-frequency components below 1000 Hz to isolate high-frequency fault signatures
noise_removal_action = {
    "tool_name": "highpass_filter",
    "params": {
        "data": loaded_data,
        "output_image_path": "./outputs/highpass_1000Hz.png",
        "cutoff_freq": 1000,
        "order": 4
    },
    "output_variable": "high_freq_signal"
}
```

### Example 2: Detrending Before FFT
```python
# Remove DC offset and slow drift before spectral analysis
detrended_signal = highpass_filter(
    data=raw_vibration_data,
    output_image_path="./plots/detrended_signal.png",
    cutoff_freq=0.5,  # Very low cutoff for detrending
    order=2
)
```

### Example 3: Enhancing Impacts in Bearing Signals
```python
# Apply highpass filter to emphasize high-frequency impacts from a bearing defect
impact_enhanced = highpass_filter(
    data=vibration_data,
    output_image_path="./plots/impact_enhanced.png",
    cutoff_freq=5000,
    order=6
)
```

These filtered signals can then be passed to tools like `create_fft_spectrum`, `create_envelope_spectrum`, or `decompose_matrix_nmf` for further analysis.

**Section sources**
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L46-L62)

## Common Pitfalls and Best Practices
### Attenuation Near Cutoff Frequency
- **Issue**: Frequencies near the cutoff are only partially attenuated, especially with lower-order filters.
- **Solution**: Use a higher filter order (e.g., 6–8) or set the cutoff frequency well below the frequency band of interest to ensure sufficient attenuation.

### Ringing Artifacts
- **Issue**: High-order filters or sharp cutoffs can cause ringing (Gibbs phenomenon) around transients.
- **Solution**: Use moderate filter orders (4–6) and avoid excessively sharp transitions. Consider using a Chebyshev or elliptic filter if steeper roll-off is needed with controlled ripple.

### Transition Width and Filter Order
- **Guideline**: A higher order provides a steeper roll-off but increases computational cost and risk of numerical instability.
- **Recommendation**: Start with order 4 and increase only if necessary. Validate stability by checking for overflow or unexpected oscillations.

### Cutoff Frequency Selection
- **Rule of Thumb**: Set the cutoff frequency at least 2–3× the highest unwanted low-frequency component (e.g., 3× shaft RPM frequency).
- **Validation**: Always inspect the filtered signal in both time and frequency domains to ensure desired components are preserved.

**Section sources**
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L11-L20)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L80-L90)

## Performance Tips for Large-Scale Signal Processing
- **Batch Processing**: When filtering multiple signals, reuse filter coefficients if the sampling rate and cutoff are identical to avoid redundant `butter()` calls.
- **Memory Efficiency**: For very long signals, consider processing in chunks if memory usage becomes a bottleneck.
- **Plotting Overhead**: Disable plotting (`output_image_path=None`) in production pipelines to reduce I/O and improve speed.
- **Vectorization**: Ensure input signals are NumPy arrays for optimal performance with `scipy` functions.
- **Parallelization**: Use multiprocessing or threading when filtering independent signals across multiple channels or datasets.

These optimizations are crucial when scaling to large datasets or real-time monitoring systems.

**Section sources**
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L110-L130)