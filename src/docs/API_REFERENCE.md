# AIDA Python API Reference

This document summarizes the public functions and classes across the AIDA codebase (src/), based on in-code docstrings.

Note: This is a static summary. For complete details, see the source files and docstrings in the repository.

---

## Application

- src/app.py
  - Module: Application entry point for AIDA (AI-Driven Analyzer)

## Core

- src/core/authentication.py
  - get_credentials() -> bool
    - Validate Google Generative AI credentials by setting env vars and instantiating a model.

- src/core/LLMOrchestrator.py
  - class LLMOrchestrator
    - run_analysis_pipeline() -> None
    - extract_text_and_json(response_string: str) -> tuple[str, dict | None]
    - _generate_content_with_fallback(prompt: str) -> genai.GenerativeModel.Response
    - _create_metaknowledge() -> None
    - _fetch_next_action(evaluation: str) -> dict
    - _execute_current_pipeline() -> dict
    - _evaluate_result(result: dict, action_taken: dict) -> str
    - _attempt_refinement(last_action: dict, evaluation: str) -> bool
    - _is_analysis_complete(last_result: dict, last_action: dict) -> bool
    - _get_available_tools(tools_dir: str = 'src/tools') -> list[str]
    - _translate_actions_to_code() -> str

- src/core/prompt_assembler.py
  - class PromptAssembler
    - build_prompt(prompt_type: str, context_bundle: dict) -> str | list
    - get_metaknowledge_json_schema_as_string() -> str

- src/core/quantitative_parameterization_module.py
  - calculate_quantitative_metrics(tool_output: dict) -> dict
  - (internal helpers)
    - _calculate_timeseries_stats(data_dict: dict) -> dict
    - _calculate_spectrum_stats(data_dict: dict) -> dict
    - _calculate_spectrogram_stats(data_dict: dict) -> dict
    - _calculate_cyclomap_stats(data_dict: dict) -> dict
    - _calculate_nmf_stats(data_dict: dict) -> dict

- src/core/rag_builder.py
  - class RAGBuilder
    - build_index(knowledge_base_paths: list[str], queue, persist_directory: str, embedding_model: str = 'all-MiniLM-L12-v2') -> Chroma
    - load_index(persist_directory: str = './vector_store') -> Chroma

## GUI

- src/gui/main_window.py
  - class App(ctk.CTk)
    - on_start_analysis() -> None
    - on_build_rag_index() -> None
    - on_load_rag_index() -> None
    - load_data_file() -> None
    - process_queue() -> None
    - (helpers) _create_* panel, _find_data_variables, _display_image_on_plot_canvas, _add_flowchart_step, _on_flowchart_click

## Tools

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
