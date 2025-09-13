# Industrial Vibration Monitoring

<cite>
**Referenced Files in This Document**   
- [baseline_measurement.py](file://baseline_measurement.py)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py)
- [create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py)
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document provides a comprehensive guide to industrial vibration monitoring using the AIDA (AI-Driven Analyzer) system. The system leverages autonomous AI orchestration to analyze vibration signals from industrial equipment such as pumps, motors, and compressors. By combining signal processing tools with Large Language Model (LLM) decision-making, AIDA establishes baseline operating profiles, detects deviations, and generates actionable insights for maintenance workflows. The documentation covers both continuous and periodic monitoring use cases, explaining how the system uses various components to create effective monitoring pipelines.

## Project Structure
The AIDA system follows a modular architecture with well-defined components organized in a hierarchical directory structure. The core functionality is separated into distinct modules for better maintainability and extensibility.

```mermaid
graph TD
A[Root Directory] --> B[src]
A --> C[Configuration Files]
A --> D[Documentation]
A --> E[Data Files]
B --> F[core]
B --> G[tools]
B --> H[gui]
B --> I[lib]
B --> J[prompt_templates]
F --> K[LLMOrchestrator.py]
F --> L[quantitative_parameterization_module.py]
F --> M[ContextManager.py]
F --> N[prompt_assembler.py]
F --> O[rag_builder.py]
G --> P[sigproc]
G --> Q[transforms]
G --> R[decomposition]
G --> S[utils]
P --> T[bandpass_filter.py]
P --> U[highpass_filter.py]
P --> V[lowpass_filter.py]
Q --> W[create_fft_spectrum.py]
Q --> X[create_envelope_spectrum.py]
Q --> Y[create_signal_spectrogram.py]
Q --> Z[create_csc_map.py]
C --> AA[mcpsettings.json]
C --> AB[baseline_results.json]
D --> AC[README.md]
D --> AD[PROJECT_DESCRIPTION.md]
D --> AE[concept.md]
E --> AF[baseline_measurement.py]
```

**Diagram sources**
- [README.md](file://README.md#L0-L244)
- [PROJECT_DESCRIPTION.md](file://PROJECT_DESCRIPTION.md#L0-L393)

**Section sources**
- [README.md](file://README.md#L0-L244)
- [PROJECT_DESCRIPTION.md](file://PROJECT_DESCRIPTION.md#L0-L393)

## Core Components
The AIDA system comprises several core components that work together to enable autonomous vibration analysis. These components include the LLM Orchestrator for decision-making, the quantitative parameterization module for statistical analysis, and various signal processing tools for data transformation.

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L0-L725)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L0-L1075)

## Architecture Overview
The AIDA system follows a modular architecture that enables autonomous analysis of vibration signals through AI-driven decision making. The system integrates LLM capabilities with signal processing tools to create an intelligent monitoring solution.

```mermaid
graph TD
A[User Input] --> B[Metaknowledge Construction]
B --> C[Initial Pipeline]
C --> D[Iterative Execution]
D --> E[Script Generation]
F[Data Files] --> B
G[Description] --> B
H[Objectives] --> B
I[Structured JSON] --> B
J[Analysis Context] --> B
K[Domain Knowledge] --> B
L[Action List] --> C
M[Tool Sequence] --> C
N[Parameters] --> C
O[Python Code] --> D
P[Subprocess Execution] --> D
Q[State Management] --> D
R[Results] --> E
S[Visualizations] --> E
T[Executable Script] --> E
```

**Diagram sources**
- [PROJECT_DESCRIPTION.md](file://PROJECT_DESCRIPTION.md#L100-L120)

## Detailed Component Analysis

### Baseline Measurement System
The baseline measurement system establishes normal operating profiles for industrial equipment by analyzing vibration signals and recording key performance metrics.

```mermaid
flowchart TD
A[Start Baseline Measurement] --> B[Setup Authentication]
B --> C[Load Test Data]
C --> D[Prepare Loaded Data]
D --> E[Create Mock Log Queue]
E --> F[Initialize LLM Orchestrator]
F --> G[Measure Initial Memory]
G --> H[Run Analysis Pipeline]
H --> I[Calculate Execution Time]
I --> J[Measure Final Memory]
J --> K[Calculate Memory Increase]
K --> L[Save Results to JSON]
L --> M[End]
C --> C1[Load MAT File]
C1 --> C2[Extract Signal Data]
C2 --> C3[Handle Missing Data]
C3 --> C4[Use Synthetic Data]
F --> F1[Set User Description]
F1 --> F2[Set User Objective]
F2 --> F3[Configure Run ID]
L --> L1[Execution Time]
L1 --> L2[Initial Memory]
L2 --> L3[Final Memory]
L3 --> L4[Memory Increase]
L4 --> L5[Success Status]
```

**Diagram sources**
- [baseline_measurement.py](file://baseline_measurement.py#L0-L173)

**Section sources**
- [baseline_measurement.py](file://baseline_measurement.py#L0-L173)

### Quantitative Parameterization Module
The quantitative parameterization module provides domain-specific metrics for different signal representations, enabling objective comparison across measurement sessions.

```mermaid
classDiagram
class calculate_quantitative_metrics {
+tool_output : Dict[str, Any]
-domain_handlers : Dict[str, Callable]
+calculate_quantitative_metrics(tool_output) Dict[str, Any]
}
class _calculate_timeseries_stats {
+data_dict : Dict[str, Any]
+_calculate_timeseries_stats(data_dict) Dict[str, float]
}
class _calculate_spectrum_stats {
+data_dict : Dict[str, Any]
+_calculate_spectrum_stats(data_dict) Dict[str, float]
}
class _calculate_spectrogram_stats {
+data_dict : Dict[str, Any]
+_calculate_spectrogram_stats(data_dict) Dict[str, Any]
}
class _calculate_cyclomap_stats {
+data_dict : Dict[str, Any]
+_calculate_cyclomap_stats(data_dict) Dict[str, Any]
}
class _calculate_nmf_stats {
+data_dict : Dict[str, Any]
+_calculate_nmf_stats(data_dict) Dict[str, Any]
}
calculate_quantitative_metrics --> _calculate_timeseries_stats : "dispatches to"
calculate_quantitative_metrics --> _calculate_spectrum_stats : "dispatches to"
calculate_quantitative_metrics --> _calculate_spectrogram_stats : "dispatches to"
calculate_quantitative_metrics --> _calculate_cyclomap_stats : "dispatches to"
calculate_quantitative_metrics --> _calculate_nmf_stats : "dispatches to"
class _extract_ids_from_path {
+image_path : Optional[str]
+_extract_ids_from_path(image_path) Tuple[Optional[str], Optional[int]]
}
class _get_fft_frequencies {
+signal_length : int
+sampling_rate : float
+_get_fft_frequencies(signal_length, sampling_rate) np.ndarray
}
class _calculate_band_energy {
+spectrum : np.ndarray
+freq_axis : np.ndarray
+freq_band : Tuple[float, float]
+_calculate_band_energy(spectrum, freq_axis, freq_band) float
}
class calculate_gini_index {
+array : np.ndarray
+calculate_gini_index(array) float
}
class estimate_alpha_stable {
+array : np.ndarray
+estimate_alpha_stable(array) float
}
class _smooth_spectrum {
+spectrum : np.ndarray
+window_size : int
+_smooth_spectrum(spectrum, window_size) np.ndarray
}
class _find_peaks {
+spectrum : np.ndarray
+min_prominence : float
+_find_peaks(spectrum, min_prominence) np.ndarray
}
class normalize_data {
+data : np.ndarray
+epsilon : float
+normalize_data(data, epsilon) np.ndarray
}
```

**Diagram sources**
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L0-L1075)

**Section sources**
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L0-L1075)

### LLM Orchestrator Analysis
The LLM Orchestrator manages the end-to-end autonomous analysis pipeline, coordinating between user objectives, tool execution, and result evaluation.

```mermaid
sequenceDiagram
participant User as "User"
participant Orchestrator as "LLMOrchestrator"
participant LLM as "Google Gemini"
participant Tools as "Signal Processing Tools"
participant GUI as "GUI Interface"
User->>Orchestrator : Define analysis objective
Orchestrator->>Orchestrator : Initialize components
Orchestrator->>Orchestrator : Create metaknowledge
Orchestrator->>Orchestrator : Load tools reference
Orchestrator->>Orchestrator : Execute initial action
Orchestrator->>GUI : Update flowchart
Orchestrator->>LLM : Request next action
LLM-->>Orchestrator : Return action proposal
Orchestrator->>Orchestrator : Add action to pipeline
Orchestrator->>Orchestrator : Execute current pipeline
Orchestrator->>Tools : Execute tool sequence
Tools-->>Orchestrator : Return results
Orchestrator->>GUI : Display results
Orchestrator->>LLM : Evaluate results
LLM-->>Orchestrator : Return evaluation
Orchestrator->>Orchestrator : Check termination
loop Main Analysis Loop
Orchestrator->>LLM : Request next action
LLM-->>Orchestrator : Return action proposal
Orchestrator->>Orchestrator : Add action to pipeline
Orchestrator->>Orchestrator : Execute current pipeline
Orchestrator->>Tools : Execute tool sequence
Tools-->>Orchestrator : Return results
Orchestrator->>GUI : Display results
Orchestrator->>LLM : Evaluate results
LLM-->>Orchestrator : Return evaluation
Orchestrator->>Orchestrator : Check if useful
alt Action not useful
Orchestrator->>Orchestrator : Remove last action
else Action useful
Orchestrator->>Orchestrator : Continue
end
Orchestrator->>Orchestrator : Check if final
end
Orchestrator->>GUI : Complete analysis
Orchestrator->>User : Return results and script
```

**Diagram sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L0-L725)

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L0-L725)

### FFT Spectrum Generation
The FFT spectrum generation tool converts time-domain vibration signals into frequency-domain representations for spectral analysis.

```mermaid
flowchart TD
A[Input Signal] --> B[Extract Parameters]
B --> C[Validate Input]
C --> D[Handle Empty Input]
D --> E[Compute FFT]
E --> F[Calculate Frequencies]
F --> G[Create One-Sided Spectrum]
G --> H[Scale Amplitudes]
H --> I[Generate Plot]
I --> J[Save Visualization]
J --> K[Return Results]
B --> B1[Get primary_data]
B1 --> B2[Get signal_data]
B2 --> B3[Get sampling_rate]
E --> E1[Apply Hanning Window]
E1 --> E2[Zero-Pad to Power of Two]
E2 --> E3[Normalize by N]
F --> F1[Use fftfreq]
F1 --> F2[Sample spacing 1/sampling_rate]
G --> G1[Take first half N//2]
G1 --> G2[Keep positive frequencies]
H --> H1[Multiply by 2]
H1 --> H2[Except DC component]
I --> I1[Create figure]
I1 --> I2[Plot spectrum]
I2 --> I3[Add grid]
I3 --> I4[Add labels]
I4 --> I5[Adjust layout]
J --> J1[Ensure directory exists]
J1 --> J2[Save plot]
J2 --> J3[Pickle figure]
K --> K1[frequencies]
K1 --> K2[amplitudes]
K2 --> K3[domain]
K3 --> K4[primary_data]
K4 --> K5[secondary_data]
K5 --> K6[image_path]
```

**Diagram sources**
- [create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py#L0-L199)

**Section sources**
- [create_fft_spectrum.py](file://src/tools/transforms/create_fft_spectrum.py#L0-L199)

### Bandpass Filtering System
The bandpass filtering system isolates specific frequency bands of interest from vibration signals, enabling targeted analysis of equipment components.

```mermaid
flowchart TD
A[Input Signal] --> B[Extract Parameters]
B --> C[Validate Input]
C --> D[Design Filter]
D --> E[Apply Filter]
E --> F[Generate Plot]
F --> G[Save Visualization]
G --> H[Return Results]
B --> B1[Get input_signal]
B1 --> B2[Get sampling_rate]
B2 --> B3[Get lowcut_freq]
B3 --> B4[Get highcut_freq]
B4 --> B5[Get order]
D --> D1[Calculate Nyquist frequency]
D1 --> D2[Normalize cutoff frequencies]
D2 --> D3[Design Butterworth filter]
D3 --> D4[Get filter coefficients]
E --> E1[Apply forward-backward filtering]
E1 --> E2[Use filtfilt function]
E2 --> E3[Zero-phase distortion]
F --> F1[Create time-domain plot]
F1 --> F2[Plot original signal]
F2 --> F3[Plot filtered signal]
F3 --> F4[Add legend]
F4 --> F5[Add grid]
F5 --> F6[Add labels]
F6 --> F7[Adjust layout]
G --> G1[Ensure directory exists]
G1 --> G2[Save plot]
G2 --> G3[Pickle figure]
H --> H1[filtered_signal]
H1 --> H2[domain]
H2 --> H3[primary_data]
H3 --> H4[image_path]
H4 --> H5[filter_characteristics]
```

**Diagram sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py)

**Section sources**
- [bandpass_filter.py](file://src/tools/sigproc/bandpass_filter.py)

## Dependency Analysis
The AIDA system has a well-defined dependency structure that enables modular development and easy extension of functionality. The core components depend on various external libraries and internal modules to provide comprehensive vibration analysis capabilities.

```mermaid
graph TD
A[LLMOrchestrator] --> B[Google Gemini API]
A --> C[LangChain]
A --> D[ChromaDB]
A --> E[scipy]
A --> F[numpy]
A --> G[matplotlib]
H[quantitative_parameterization_module] --> E
H --> F
H --> G
H --> I[scipy.stats]
H --> J[src.lib.rlowess_smoother]
K[create_fft_spectrum] --> E
K --> F
K --> G
L[bandpass_filter] --> E
L --> F
L --> G
M[create_envelope_spectrum] --> E
M --> F
M --> G
N[create_signal_spectrogram] --> E
N --> F
N --> G
O[create_csc_map] --> E
O --> F
O --> G
P[decompose_matrix_nmf] --> F
P --> Q[sklearn.decomposition]
R[select_component] --> F
S[load_data] --> T[scipy.io]
S --> F
A --> H
A --> K
A --> L
A --> M
A --> N
A --> O
A --> P
A --> R
A --> S
```

**Diagram sources**
- [requirements.txt](file://requirements.txt)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L0-L725)

## Performance Considerations
The AIDA system is designed with performance in mind, balancing computational efficiency with analytical accuracy. The system typically requires 2-5 minutes per analysis pipeline with memory usage ranging from 500MB to 2GB depending on data size. The token consumption for LLM interactions ranges from 10K to 50K tokens per analysis, supporting signals with up to 1 million samples. The system uses subprocess execution with timeout protection to prevent hanging processes, and implements state persistence through pickle-based serialization between pipeline steps. For large datasets, the system employs efficient FFT algorithms with zero-padding to the next power of two for optimal performance. The RAG (Retrieval-Augmented Generation) system uses ChromaDB with persistent storage for fast knowledge retrieval, reducing the need for repeated LLM queries. The modular tool architecture allows for selective loading of only the required components, minimizing memory footprint for specific analysis tasks.

**Section sources**
- [PROJECT_DESCRIPTION.md](file://PROJECT_DESCRIPTION.md#L300-L320)

## Troubleshooting Guide
When encountering issues with the AIDA system, follow these troubleshooting steps to identify and resolve common problems:

```mermaid
flowchart TD
A[Problem Identified] --> B[Check Authentication]
B --> C[Verify Gemini API Key]
C --> D[Check Environment Variables]
D --> E[Test API Connectivity]
E --> F{Resolved?}
F --> |Yes| G[Continue Analysis]
F --> |No| H[Check Dependencies]
H --> I[Verify requirements.txt]
I --> J[Reinstall Packages]
J --> K[Test Installation]
K --> L{Resolved?}
L --> |Yes| G
L --> |No| M[Check Vector Store]
M --> N[Verify vector_store Directory]
N --> O[Rebuild Knowledge Base]
O --> P[Run RAG Builder]
P --> Q{Resolved?}
Q --> |Yes| G
Q --> |No| R[Check Data Format]
R --> S[Validate Input Files]
S --> T[Check Signal Data]
T --> U[Verify Sampling Rate]
U --> V{Resolved?}
V --> |Yes| G
V --> |No| W[Examine Logs]
W --> X[Check log_queue Output]
X --> Y[Review Error Messages]
Y --> Z[Search Documentation]
Z --> AA{Resolved?}
AA --> |Yes| G
AA --> |No| AB[Submit Issue]
AB --> AC[GitHub Repository]
```

**Diagram sources**
- [README.md](file://README.md#L200-L244)

**Section sources**
- [README.md](file://README.md#L200-L244)

## Conclusion
The AIDA system provides a comprehensive solution for industrial vibration monitoring by combining autonomous AI decision-making with advanced signal processing techniques. The system's ability to establish baseline operating profiles through the baseline_measurement.py script enables effective deviation detection in continuous and periodic monitoring scenarios. By leveraging the quantitative_parameterization_module.py, the system provides objective metrics for comparing measurement sessions across different equipment types. The autonomous pipeline generation for FFT-based spectral trending, combined with bandpass filtering to isolate frequency bands of interest, creates a powerful analysis framework. The LLMOrchestrator adapts analysis strategies based on equipment type and operating conditions, demonstrating the system's flexibility. Automated report generation and threshold-based alerting integrate seamlessly with maintenance workflows, while the modular architecture allows for easy extension with additional tools. The system's design supports long-term data storage considerations through structured result serialization and persistent state management. Overall, AIDA represents a significant advancement in industrial vibration monitoring, providing a scalable, intelligent solution for predictive maintenance applications.