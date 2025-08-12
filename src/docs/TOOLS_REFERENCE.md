### utils
- src/tools/utils/load_data.py
  - load_data(signal_data: np.ndarray, sampling_rate: int, output_image_path: str) -> dict

### sigproc
- src/tools/sigproc/lowpass_filter.py
  - lowpass_filter(data: dict, output_image_path: str, cutoff_freq: float = 3500, order: int = 4) -> dict
- src/tools/sigproc/highpass_filter.py
  - highpass_filter(data: dict, output_image_path: str, cutoff_freq: float = 3500, order: int = 4) -> dict
- src/tools/sigproc/bandpass_filter.py
  - bandpass_filter(data: dict, output_image_path: str, lowcut_freq: float = 1000, highcut_freq: float = 4000, order: int = 4) -> dict

### transforms
- src/tools/transforms/create_signal_spectrogram.py
  - create_signal_spectrogram(data: dict, output_image_path: str, window: int = 1024, noverlap: int = 800) -> dict
- src/tools/transforms/create_fft_spectrum.py
  - create_fft_spectrum(data: dict, output_image_path: str) -> dict
- src/tools/transforms/create_envelope_spectrum.py
  - create_envelope_spectrum(data: dict, output_image_path: str) -> dict
- src/tools/transforms/create_csc_map.py
  - create_csc_map(data: dict, output_image_path: str, min_alpha: int = 1, max_alpha: int = 150, window: int = 256, overlap: int = 220) -> dict

### decomposition
- src/tools/decomposition/decompose_matrix_nmf.py
  - decompose_matrix_nmf(data: dict, output_image_path: str, n_components: int = 3, max_iter: int = 150) -> dict
- src/tools/decomposition/select_component.py
  - select_component(data: dict, output_image_path: str, component_index: int) -> dict
---
For detailed input/outputs and behavior, see the docstrings in each module.