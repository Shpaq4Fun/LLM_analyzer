# Signal Processing Tools

<cite>
**Referenced Files in This Document**   
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py)
- [bandpass_filter.md](file://src/tools/sigproc/bandpass_filter.md)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py)
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md)
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py)
- [lowpass_filter.md](file://src/tools/sigproc/lowpass_filter.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Bandpass Filter](#bandpass-filter)
3. [Highpass Filter](#highpass-filter)
4. [Lowpass Filter](#lowpass-filter)
5. [Common Implementation Details](#common-implementation-details)
6. [Performance and Best Practices](#performance-and-best-practices)
7. [Troubleshooting Guide](#troubleshooting-guide)

## Introduction
This document provides comprehensive documentation for three digital signal filtering tools: `bandpass_filter`, `highpass_filter`, and `lowpass_filter`. These tools are designed for vibration and time-series signal analysis in industrial fault detection applications. Each filter isolates specific frequency components using zero-phase Butterworth designs, preserving temporal alignment while attenuating unwanted frequencies. The filters are implemented using `scipy.signal` and are optimized for diagnostic workflows such as envelope analysis and noise reduction.

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L245)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L153)

## Bandpass Filter

### Purpose and Application
The `bandpass_filter` isolates a specific frequency band by attenuating frequencies both below the lower cutoff and above the upper cutoff. It is primarily used to:
- **Isolate resonant bands** where fault-related impacts occur
- **Prepare signals for envelope analysis**, a critical step in detecting bearing faults and gear damage
- **Inspect harmonic structures** by focusing on a single carrier frequency and its sidebands

This tool is typically applied after initial spectral analysis (e.g., FFT or spectrogram) identifies a frequency band of interest.

### Function Signature and Parameters
```python
def bandpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    lowcut_freq: float = 1000.0,
    highcut_freq: float = 4000.0,
    order: int = 4,
    **kwargs
) -> Dict[str, Any]
```

**Parameter Descriptions:**
| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | Input dictionary containing signal and metadata | Yes | None |
| output_image_path | str | Path to save the filtered signal plot | Yes | None |
| lowcut_freq | float | Lower cutoff frequency (Hz) | No | 1000.0 |
| highcut_freq | float | Upper cutoff frequency (Hz) | No | 4000.0 |
| order | int | Filter order (steepness of roll-off) | No | 4 |

**Input Requirements:**
- `data` must contain:
  - `primary_data`: key name for the signal array
  - `sampling_rate`: sampling frequency in Hz
- Signal must be a 1D NumPy array of floats

**Return Value:**
Returns a dictionary with:
- `filtered_signal`: filtered time-series data
- `domain`: set to `'time-series'`
- `primary_data`: set to `'filtered_signal'`
- `sampling_rate`: original sampling rate
- `image_path`: path to generated plot
- `filter_params`: dictionary of applied filter settings

### Internal Implementation
The filter uses a zero-phase Butterworth design via `scipy.signal.butter` and `filtfilt`:
1. **Frequency Normalization**: Cutoff frequencies are normalized relative to the Nyquist frequency (half the sampling rate).
2. **Filter Design**: A digital bandpass filter is designed using `butter(N=order, Wn=[low_norm, high_norm], btype='band')`.
3. **Zero-Phase Filtering**: `filtfilt` applies the filter forward and backward to eliminate phase distortion.
4. **Edge Handling**: Padding is applied using `padlen=3*(max(len(a), len(b)) - 1)` to minimize edge effects.

Automatic validation ensures:
- `lowcut_freq < highcut_freq`
- Frequencies are within valid ranges (0 < lowcut < highcut < Nyquist)
- Invalid values trigger warnings and are adjusted

### Practical Usage Example
```python
# Isolate 2-4 kHz band for bearing fault analysis
result = bandpass_filter(
    data={
        'primary_data': 'vibration_signal',
        'vibration_signal': raw_data,
        'sampling_rate': 10000
    },
    output_image_path='./outputs/bandpassed.png',
    lowcut_freq=2000,
    highcut_freq=4000,
    order=4
)
filtered_signal = result['filtered_signal']
```

**Next Steps:**
- Apply `create_envelope_spectrum` to detect fault repetition rates
- Compute FFT to verify frequency content
- Calculate kurtosis to assess impulsiveness

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L245)
- [bandpass_filter.md](file://src/tools/sigproc/bandpass_filter.md#L1-L65)

## Highpass Filter

### Purpose and Application
The `highpass_filter` removes low-frequency components below a specified cutoff. Key applications include:
- **Removing operational noise** (e.g., 1x shaft frequency) to improve SNR for high-frequency fault detection
- **Detrending and DC offset removal** when used with very low cutoffs (e.g., 0.1–1 Hz)
- **Emphasizing transients** by acting as a differentiator, enhancing sharp impulses

### Function Signature and Parameters
```python
def highpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    cutoff_freq: float = 3500,
    order: int = 4
) -> Dict[str, Any]
```

**Parameter Descriptions:**
| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | Input dictionary containing signal and metadata | Yes | None |
| output_image_path | str | Path to save the filtered signal plot | Yes | None |
| cutoff_freq | float | Cutoff frequency (Hz) | No | 3500 |
| order | int | Filter order | No | 4 |

### Internal Implementation
- Uses `butter(N=order, Wn=cutoff_norm, btype='high')` for filter design
- Applies zero-phase filtering via `filtfilt`
- Validates that `0 < cutoff_freq < Nyquist frequency`
- Raises `ValueError` for invalid inputs

### Practical Usage Example
```python
# Remove low-frequency noise below 1 kHz
result = highpass_filter(
    data={
        'primary_data': 'signal',
        'signal': noisy_data,
        'sampling_rate': 10000
    },
    output_image_path='./outputs/highpassed.png',
    cutoff_freq=1000
)
high_freq_signal = result['filtered_signal']
```

**Next Steps:**
- Apply FFT or spectrogram to analyze high-frequency content
- Use as input for NMF decomposition
- Feed into envelope analysis if high-frequency carrier is present

**Section sources**
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [highpass_filter.md](file://src/tools/sigproc/highpass_filter.md#L1-L63)

## Lowpass Filter

### Purpose and Application
The `lowpass_filter` removes high-frequency components above a specified cutoff. Applications include:
- **Denoising** by eliminating high-frequency noise
- **Component isolation** of low-frequency signals
- **Anti-aliasing before downsampling** (mandatory step)
- **Envelope smoothing** after Hilbert transform
- **Trend extraction** using very low cutoffs (<1 Hz)

### Function Signature and Parameters
```python
def lowpass_filter(
    data: Dict[str, Any],
    output_image_path: str,
    cutoff_freq: float = 3500,
    order: int = 4
) -> Dict[str, Any]
```

**Parameter Descriptions:**
| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | Input dictionary containing signal and metadata | Yes | None |
| output_image_path | str | Path to save the filtered signal plot | Yes | None |
| cutoff_freq | float | Cutoff frequency (Hz) | No | 3500 |
| order | int | Filter order | No | 4 |

### Internal Implementation
- Uses `butter(N=order, Wn=cutoff_norm, btype='low')` for filter design
- Zero-phase filtering via `filtfilt`
- Input validation ensures valid frequency range
- Redundant variable `normal_cutoff` exists but `cutoff_norm` is used

### Practical Usage Example
```python
# Denoise signal by removing frequencies above 5 kHz
result = lowpass_filter(
    data={
        'primary_data': 'noisy_signal',
        'noisy_signal': raw_data,
        'sampling_rate': 20000
    },
    output_image_path='./outputs/denoised.png',
    cutoff_freq=5000
)
denoised_signal = result['filtered_signal']
```

**Next Steps:**
- Downsample the anti-aliased signal
- Calculate features on smoothed envelope
- Subtract trend from original for detrending

**Section sources**
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L153)
- [lowpass_filter.md](file://src/tools/sigproc/lowpass_filter.md#L1-L67)

## Common Implementation Details

### Filter Design and Stability
All three filters use:
- **Butterworth design**: Maximally flat passband, moderate roll-off
- **Zero-phase filtering**: Achieved via `filtfilt` to prevent time-domain shifts
- **Normalized frequencies**: Cutoffs scaled by Nyquist frequency (0.5 × sampling_rate)
- **Robust input validation**: Ensures physical and numerical validity

### Visualization and Output
Each filter:
- Generates a plot of the filtered signal vs. time
- Saves plots in PNG format
- Stores pickled Matplotlib figures for later inspection
- Uses consistent styling: blue lines, grid, labeled axes

### Error Handling
- Validates presence of required keys (`primary_data`, `sampling_rate`)
- Checks signal validity (non-empty, 1D array)
- Enforces frequency constraints relative to Nyquist
- Provides descriptive error messages and warnings

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L245)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L153)

## Performance and Best Practices

### Filter Order Selection
- **Order 4**: Recommended default; balances roll-off steepness and stability
- **Higher orders (>6)**: May cause numerical instability, especially at extreme frequency ratios
- **Lower orders (2–3)**: Gentler roll-off, more stable, suitable for noisy environments

### Frequency Range Guidelines
- Ensure `cutoff_freq < 0.9 × Nyquist` to avoid aliasing
- For bandpass, maintain sufficient bandwidth: `highcut_freq > 1.5 × lowcut_freq`
- Use logarithmic spacing for wideband analysis

### Real-Time and Large Data Processing
- **Precompute filter coefficients** if reusing same parameters
- **Process in chunks** for very long signals using consistent padding
- **Use `float32`** instead of `float64` to reduce memory usage when precision allows
- **Avoid redundant filtering** by caching results

### Configuration Best Practices
Link to: [TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md) for system-wide configuration guidelines.

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L245)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L153)

## Troubleshooting Guide

### Common Issues and Solutions
| Issue | Cause | Solution |
| :---- | :---- | :---- |
| **Filtered signal is zero or NaN** | Invalid frequency range or sampling rate | Validate `sampling_rate` and ensure `cutoff_freq < Nyquist` |
| **Edge artifacts** | Insufficient padding in `filtfilt` | Increase `padlen` or trim edges post-filtering |
| **No visible change** | Cutoff frequency too high/low or order too low | Adjust cutoffs and increase filter order |
| **Phase distortion observed** | Using `lfilter` instead of `filtfilt` | Ensure zero-phase filtering is enabled |
| **Performance bottlenecks** | High-order filters on large datasets | Reduce order or process in segments |

### Numerical Stability Tips
- Avoid very high filter orders (>8)
- Ensure frequency ratios are not extreme (e.g., 1 Hz cutoff at 100 kHz sampling)
- Prefer second-order sections (`output='sos'`) for critical applications (not currently implemented)

### Debugging Workflow
1. Verify input dictionary structure
2. Check sampling rate and signal length
3. Plot original vs. filtered signal
4. Inspect `filter_params` in output
5. Test with synthetic signal (e.g., sum of sines)

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L245)
- [highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L152)
- [lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L153)