# Tool Reference

<cite>
**Referenced Files in This Document**   
- [src/tools/utils/load_data.py](file://src/tools/utils/load_data.py#L1-L72)
- [src/tools/sigproc/lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L152)
- [src/tools/sigproc/highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L151)
- [src/tools/sigproc/bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L244)
- [src/tools/transforms/create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py)
- [src/tools/transforms/create_signal_spectrogram.py](file://src/tools/transforms/create_signal_spectrogram.py)
- [src/tools/transforms/create_envelope_spectrum.py](file://src/tools/transforms/create_envelope_spectrum.py)
- [src/tools/transforms/create_csc_map.py](file://src/tools/transforms/create_csc_map.py)
- [src/tools/decomposition/decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py)
- [src/tools/decomposition/select_component.py](file://src/tools/decomposition/select_component.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Utilities](#utilities)
3. [Signal Processing (Filters)](#signal-processing-filters)
4. [Transforms](#transforms)
5. [Decomposition](#decomposition)
6. [Usage Patterns and Pipelines](#usage-patterns-and-pipelines)
7. [Common Errors and Performance Tips](#common-errors-and-performance-tips)
8. [Tool Selection Guide](#tool-selection-guide)

## Introduction
This document provides comprehensive reference documentation for the analysis tools available in the LLM Analyzer project. The tools are organized into four main categories: utilities, signal processing (filters), transforms, and decomposition. Each tool is designed to be used in a modular pipeline, accepting structured input data and returning enriched output with visualizations. All tools follow a consistent interface pattern, using dictionaries to pass data between stages and generating plots for visual validation.

**Section sources**
- [src/tools/utils/load_data.py](file://src/tools/utils/load_data.py#L1-L72)

## Utilities

### load_data
Loads and visualizes raw time-series signal data.

**Label Structure Requirements**
- **signal_data**: 1D NumPy array containing the time-domain signal
- **sampling_rate**: Sampling frequency in Hz (integer)
- **output_image_path**: Filesystem path where the plot will be saved

**Returns**
- **dict** with keys:
  - `signal_data`: Trimmed input signal (first 3 seconds)
  - `sampling_rate`: Original sampling rate
  - `domain`: Set to "time-series"
  - `primary_data`: Key name of the main data field ("signal_data")
  - `image_path`: Path to the generated plot

**Behavior**
The function trims the input signal to the first 3 seconds (or full length if shorter), generates a time-series plot, and returns a standardized dictionary structure used by subsequent tools. If no data is provided, it creates an empty plot.

```python
result = load_data(
    signal_data=np.random.randn(10000),
    sampling_rate=5000,
    output_image_path="plots/time_series.png"
)
```

**Section sources**
- [src/tools/utils/load_data.py](file://src/tools/utils/load_data.py#L1-L72)

## Signal Processing (Filters)

### lowpass_filter
Applies a zero-phase Butterworth low-pass filter to attenuate high-frequency components.

**Label Structure Requirements**
- **data**: Input dictionary containing:
  - `primary_data`: Key name of the signal array
  - `sampling_rate`: Signal sampling rate in Hz
- **output_image_path**: Path to save the filtered signal plot
- **cutoff_freq**: Frequency above which signals are attenuated (default: 3500 Hz)
- **order**: Filter order (default: 4)

**Returns**
- **dict** with keys:
  - `filtered_signal`: Filtered time-domain signal
  - `domain`: "time-series"
  - `primary_data`: "filtered_signal"
  - `sampling_rate`: Original sampling rate
  - `image_path`: Path to generated plot
  - `filter_params`: Dictionary of filter parameters used

**Mathematical Foundation**
Implements a digital Butterworth filter using `scipy.signal.butter` and applies it with zero phase distortion using `filtfilt`, which filters in both forward and reverse directions.

```python
filtered = lowpass_filter(
    data=result,
    output_image_path="plots/lowpass.png",
    cutoff_freq=2000,
    order=6
)
```

**Section sources**
- [src/tools/sigproc/lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L152)

### highpass_filter
Applies a zero-phase Butterworth high-pass filter to attenuate low-frequency components.

**Label Structure Requirements**
- Same as `lowpass_filter` with identical parameters

**Returns**
- Same structure as `lowpass_filter`, with filter type set to "butterworth_highpass"

**Behavior**
Identical to `lowpass_filter` but removes frequencies below the cutoff frequency. Uses the same zero-phase filtering approach.

```python
filtered = highpass_filter(
    data=result,
    output_image_path="plots/highpass.png",
    cutoff_freq=1000,
    order=4
)
```

**Section sources**
- [src/tools/sigproc/highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L151)

### bandpass_filter
Applies a zero-phase Butterworth band-pass filter to isolate a frequency range.

**Label Structure Requirements**
- **data**: Input dictionary with signal data
- **output_image_path**: Path to save plot
- **lowcut_freq**: Lower frequency bound (default: 1000 Hz)
- **highcut_freq**: Upper frequency bound (default: 4000 Hz)
- **order**: Filter order (default: 4)

**Returns**
- **dict** with keys:
  - `filtered_signal`: Band-pass filtered signal
  - `domain`: "time-series"
  - `primary_data`: "filtered_signal"
  - `sampling_rate`: Original sampling rate
  - `image_path`: Path to generated plot
  - `filter_params`: Contains both low and high cutoff frequencies

**Validation**
Automatically validates and corrects frequency parameters:
- Ensures lowcut < highcut (swaps if necessary)
- Clips highcut below Nyquist frequency
- Ensures lowcut > 0

```python
bandpassed = bandpass_filter(
    data=result,
    output_image_path="plots/bandpass.png",
    lowcut_freq=1500,
    highcut_freq=3500,
    order=5
)
```

**Section sources**
- [src/tools/sigproc/bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L244)

## Transforms

### create_fft_spectrum
Computes the Fast Fourier Transform (FFT) of a time-domain signal.

**Label Structure Requirements**
- **data**: Dictionary containing time-series signal
- **output_image_path**: Path to save frequency spectrum plot

**Returns**
- **dict** with:
  - `frequency_spectrum`: Magnitude of FFT
  - `frequencies`: Frequency axis
  - `domain`: "frequency"
  - `primary_data`: "frequency_spectrum"
  - `image_path`: Path to spectrum plot

**Mathematical Foundation**
Uses `numpy.fft.rfft` to compute the real FFT, providing frequency content representation. The magnitude spectrum shows signal energy distribution across frequencies.

```python
fft_result = create_fft_spectrum(
    data=result,
    output_image_path="plots/fft_spectrum.png"
)
```

**Section sources**
- [src/tools/transforms/create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py)

### create_signal_spectrogram
Generates a time-frequency representation using Short-Time Fourier Transform (STFT).

**Label Structure Requirements**
- **window**: FFT window size (default: 256)
- **noverlap**: Number of overlapping samples (default: 220)

**Returns**
- **dict** with spectrogram data and time/frequency axes
- Generates a heatmap showing frequency content evolution over time

**Usage**
Ideal for analyzing non-stationary signals where frequency content changes over time.

```python
spectrogram = create_signal_spectrogram(
    data=result,
    output_image_path="plots/spectrogram.png",
    window=512,
    noverlap=480
)
```

**Section sources**
- [src/tools/transforms/create_signal_spectrogram.py](file://src/tools/transforms/create_signal_spectrogram.py)

### create_envelope_spectrum
Computes the envelope spectrum, commonly used in bearing fault detection.

**Process**
1. Applies band-pass filtering (typically around resonance frequency)
2. Computes signal envelope using Hilbert transform
3. Takes FFT of the envelope signal

**Returns**
- Envelope spectrum highlighting fault-related frequencies

**Application**
Used for detecting periodic impacts in machinery vibration signals.

```python
envelope = create_envelope_spectrum(
    data=result,
    output_image_path="plots/envelope_spectrum.png"
)
```

**Section sources**
- [src/tools/transforms/create_envelope_spectrum.py](file://src/tools/transforms/create_envelope_spectrum.py)

### create_csc_map
Generates a Constant Spectral Chirp (CSC) map for time-frequency analysis.

**Label Structure Requirements**
- **min_alpha**, **max_alpha**: Chirp rate range
- **window**, **overlap**: STFT parameters

**Returns**
- Time-frequency representation optimized for chirp signal detection

**Application**
Useful for analyzing signals with rapidly changing frequencies.

```python
csc_map = create_csc_map(
    data=result,
    output_image_path="plots/csc_map.png",
    min_alpha=1,
    max_alpha=100
)
```

**Section sources**
- [src/tools/transforms/create_csc_map.py](file://src/tools/transforms/create_csc_map.py)

## Decomposition

### decompose_matrix_nmf
Performs Non-Negative Matrix Factorization (NMF) on spectral data.

**Label Structure Requirements**
- **n_components**: Number of basis components to extract (default: 3)
- **max_iter**: Maximum iterations for convergence (default: 150)

**Mathematical Foundation**
Decomposes a non-negative matrix V into two non-negative matrices W and H such that V ≈ WH. W represents basis spectra and H represents activation coefficients.

**Returns**
- **dict** with:
  - `basis_components`: Matrix W
  - `activations`: Matrix H
  - `reconstructed`: WH product
  - `image_path`: Visualization of components

**Application**
Used to separate mixed signal sources or identify recurring spectral patterns.

```python
nmf_result = decompose_matrix_nmf(
    data=spectrogram,
    output_image_path="plots/nmf_decomposition.png",
    n_components=4
)
```

**Section sources**
- [src/tools/decomposition/decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py)

### select_component
Extracts a specific component from a decomposition result.

**Label Structure Requirements**
- **component_index**: Zero-based index of the component to extract

**Returns**
- Single isolated component with standardized dictionary structure
- Enables focused analysis of individual components

```python
selected = select_component(
    data=nmf_result,
    output_image_path="plots/selected_component.png",
    component_index=1
)
```

**Section sources**
- [src/tools/decomposition/select_component.py](file://src/tools/decomposition/select_component.py)

## Usage Patterns and Pipelines

### Basic Analysis Pipeline
```python
# Load and visualize raw data
raw = load_data(signal, fs, "plots/raw.png")

# Apply bandpass filter to isolate frequency band of interest
filtered = bandpass_filter(raw, "plots/bandpass.png", 1000, 4000)

# Generate spectrogram to visualize time-frequency content
spec = create_signal_spectrogram(filtered, "plots/spectrogram.png")

# Compute envelope spectrum for fault detection
env = create_envelope_spectrum(filtered, "plots/envelope.png")
```

### Source Separation Pipeline
```python
# Decompose spectrogram into components
nmf = decompose_matrix_nmf(spec, "plots/nmf.png", n_components=3)

# Select and analyze individual components
comp1 = select_component(nmf, "plots/component1.png", 0)
comp2 = select_component(nmf, "plots/component2.png", 1)
```

**Section sources**
- [src/tools/utils/load_data.py](file://src/tools/utils/load_data.py#L1-L72)
- [src/tools/sigproc/bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L244)
- [src/tools/transforms/create_signal_spectrogram.py](file://src/tools/transforms/create_signal_spectrogram.py)
- [src/tools/transforms/create_envelope_spectrum.py](file://src/tools/transforms/create_envelope_spectrum.py)
- [src/tools/decomposition/decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py)
- [src/tools/decomposition/select_component.py](file://src/tools/decomposition/select_component.py)

## Common Errors and Performance Tips

### Common Errors
- **Missing primary_data key**: Always ensure input dictionaries contain the `primary_data` field pointing to the signal array
- **Invalid frequency ranges**: Cutoff frequencies must be positive and below Nyquist frequency (sampling_rate/2)
- **Empty signal data**: Verify signal arrays are not empty before processing
- **File path issues**: Ensure output directories exist or are creatable

### Performance Tips
- **Filter order**: Use lower orders (4-6) for real-time applications; higher orders provide sharper roll-off but increase computation
- **Window size**: Larger windows in spectrogram provide better frequency resolution; smaller windows improve time resolution
- **NMF convergence**: Increase max_iter for better convergence, but monitor computation time
- **Memory management**: The pipeline generates multiple plot files; clean up intermediate results when processing large datasets

**Section sources**
- [src/tools/sigproc/lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L152)
- [src/tools/sigproc/highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L151)
- [src/tools/sigproc/bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L244)
- [src/tools/transforms/create_signal_spectrogram.py](file://src/tools/transforms/create_signal_spectrogram.py)
- [src/tools/decomposition/decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py)

## Tool Selection Guide

### Signal Processing (Filters)
- **lowpass_filter**: Remove high-frequency noise
- **highpass_filter**: Eliminate DC offset or low-frequency drift
- **bandpass_filter**: Isolate specific frequency bands (e.g., bearing fault frequencies)

### Transforms
- **create_fft_spectrum**: Analyze stationary signal frequency content
- **create_signal_spectrogram**: Examine time-varying frequency behavior
- **create_envelope_spectrum**: Detect periodic impacts in machinery
- **create_csc_map**: Analyze chirp-like signals with rapid frequency changes

### Decomposition
- **decompose_matrix_nmf**: Separate mixed sources or identify patterns
- **select_component**: Focus analysis on specific extracted components

### Utilities
- **load_data**: Initialize analysis with raw time-series data

**Selection Criteria**
- Start with `load_data` to initialize the pipeline
- Apply appropriate filter based on frequency characteristics of interest
- Use FFT for stationary signals, spectrogram for non-stationary signals
- Apply envelope spectrum when searching for repetitive impacts
- Use NMF when signals contain multiple overlapping sources

**Section sources**
- [src/tools/utils/load_data.py](file://src/tools/utils/load_data.py#L1-L72)
- [src/tools/sigproc/lowpass_filter.py](file://src/tools/sigproc/lowpass_filter.py#L1-L152)
- [src/tools/sigproc/highpass_filter.py](file://src/tools/sigproc/highpass_filter.py#L1-L151)
- [src/tools/sigproc/bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py#L1-L244)
- [src/tools/transforms/create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py)
- [src/tools/transforms/create_signal_spectrogram.py](file://src/tools/transforms/create_signal_spectrogram.py)
- [src/tools/transforms/create_envelope_spectrum.py](file://src/tools/transforms/create_envelope_spectrum.py)
- [src/tools/transforms/create_csc_map.py](file://src/tools/transforms/create_csc_map.py)
- [src/tools/decomposition/decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py)
- [src/tools/decomposition/select_component.py](file://src/tools/decomposition/select_component.py)