# Component Selection

<cite>
**Referenced Files in This Document**   
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)
- [decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py#L1-L195)
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
This document provides comprehensive documentation for the component selection module within the LLM-based signal analysis system. The module is responsible for selecting specific components derived from non-negative matrix factorization (NMF) based on diagnostic relevance. It interfaces with quantitative parameterization and orchestration components to enable autonomous fault diagnosis in mechanical systems. The system leverages an LLM orchestrator to autonomously decide which signal processing tools to apply and which components to select for further analysis.

## Project Structure
The project follows a modular architecture with distinct directories for core logic, tools, GUI components, and documentation. The component selection functionality resides in the decomposition tools module, while higher-level orchestration and decision-making are handled by the core modules.

```mermaid
graph TD
src[src/] --> core[core/]
src --> tools[tools/]
src --> docs[docs/]
src --> gui[gui/]
src --> lib[lib/]
src --> prompt_templates[prompt_templates/]
core --> ContextManager[ContextManager.py]
core --> LLMOrchestrator[LLMOrchestrator.py]
core --> quantitative_parameterization_module[quantitative_parameterization_module.py]
core --> prompt_assembler[prompt_assembler.py]
core --> rag_builder[rag_builder.py]
tools --> decomposition[decomposition/]
tools --> sigproc[sigproc/]
tools --> transforms[transforms/]
tools --> utils[utils/]
decomposition --> select_component[select_component.py]
decomposition --> decompose_matrix_nmf[decompose_matrix_nmf.py]
```

**Diagram sources**
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py#L1-L195)

**Section sources**
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py#L1-L195)

## Core Components
The core components of the system include the LLM orchestrator, which manages the analysis workflow, the quantitative parameterization module that computes diagnostic metrics, and the component selection tool that extracts specific NMF components. These components work together to enable autonomous signal analysis and fault detection.

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)

## Architecture Overview
The system architecture follows a pipeline-based approach where the LLM orchestrator sequentially applies signal processing tools, evaluates results, and decides on subsequent actions. The component selection module is a key part of this pipeline, allowing the system to focus on specific components identified as potentially diagnostic.

```mermaid
graph TD
User[User Input] --> Orchestrator[LLMOrchestrator]
Orchestrator --> Tools[Tool Library]
Tools --> Decomposition[decomposition/]
Tools --> Transforms[transforms/]
Tools --> Sigproc[sigproc/]
Decomposition --> NMF[decompose_matrix_nmf.py]
Decomposition --> Select[select_component.py]
NMF --> Components[NMF Components]
Components --> Select
Select --> Selected[Selected Component]
Selected --> Quantitative[quantitative_parameterization_module.py]
Quantitative --> Metrics[Diagnostic Metrics]
Metrics --> Orchestrator
Orchestrator --> Decision[Next Action Decision]
Decision --> Tools
style Orchestrator fill:#f9f,stroke:#333
style Quantitative fill:#bbf,stroke:#333
```

**Diagram sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)

## Detailed Component Analysis

### Component Selection Module Analysis
The component selection module provides functionality to extract specific components from NMF-decomposed signals. It serves as a bridge between decomposition and further analysis, enabling focused examination of individual components.

#### Function Implementation
```python
def select_component(
    data: Dict[str, Any],
    output_image_path: str,
    component_index: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Select and extract a specific component from a set of reconstructed signals.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing:
        - 'new_params': Dict[str, Any] with 'signals_reconstructed' key
        - 'sampling_rate': float, signal sampling rate in Hz
    output_image_path : str
        Path to save visualization of selected component
    component_index : int
        Zero-based index of component to select
    **kwargs
        Additional keyword arguments for future extensions

    Returns
    -------
    Dict[str, Any]
        Dictionary with selected component data and metadata
    """
```

**Section sources**
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)

### Quantitative Parameterization Module
The quantitative parameterization module computes diagnostic metrics from signal representations, providing the LLM with quantitative information to guide component selection.

#### Metric Calculation Flow
```mermaid
flowchart TD
Input[Input Data] --> DomainCheck{Domain Check}
DomainCheck --> |time-series| TimeSeries[_calculate_timeseries_stats]
DomainCheck --> |frequency-spectrum| FreqSpectrum[_calculate_spectrum_stats]
DomainCheck --> |time-frequency-matrix| Spectrogram[_calculate_spectrogram_stats]
DomainCheck --> |bi-frequency-matrix| Cyclomap[_calculate_cyclomap_stats]
DomainCheck --> |decomposed_matrix| NMF[_calculate_nmf_stats]
TimeSeries --> Kurtosis[Kurtosis]
TimeSeries --> Skewness[Skewness]
TimeSeries --> RMS[Root Mean Square]
TimeSeries --> Crest[Crest Factor]
FreqSpectrum --> Dominant[Dom. Frequency]
FreqSpectrum --> Centroid[Spectral Centroid]
Spectrogram --> Gini[Gini Index]
Spectrogram --> SkewSelector[Skewness Selector]
Spectrogram --> JBSelector[Jarque-Bera Selector]
Cyclomap --> MaxCoherence[Max Coherence]
Cyclomap --> PeakFreq[Peak Frequencies]
NMF --> Sparsity[Sparsity Metrics]
NMF --> Periodicity[Periodicity Measures]
Kurtosis --> Output[Output Metrics]
Skewness --> Output
RMS --> Output
Crest --> Output
Dominant --> Output
Centroid --> Output
Gini --> Output
SkewSelector --> Output
JBSelector --> Output
MaxCoherence --> Output
PeakFreq --> Output
Sparsity --> Output
Periodicity --> Output
```

**Diagram sources**
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)

**Section sources**
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)

### LLM Orchestrator Integration
The LLM orchestrator manages the end-to-end analysis pipeline, deciding when to decompose signals and which components to select based on diagnostic relevance.

#### Action Selection Sequence
```mermaid
sequenceDiagram
participant User
participant Orchestrator
participant Tools
participant LLM
User->>Orchestrator : Start Analysis
Orchestrator->>LLM : Build Initial Prompt
LLM->>Orchestrator : Propose First Action
Orchestrator->>Tools : Execute Action (e.g., load_data)
Tools->>Orchestrator : Return Results
Orchestrator->>LLM : Evaluate Results
LLM->>Orchestrator : Propose Next Action
alt Need Decomposition
Orchestrator->>Tools : decompose_matrix_nmf
Tools->>Orchestrator : Return Components
Orchestrator->>LLM : Evaluate Components
LLM->>Orchestrator : Propose Component Selection
Orchestrator->>Tools : select_component
Tools->>Orchestrator : Return Selected Component
else Final Analysis
Orchestrator->>User : Present Results
end
```

**Diagram sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)

## Dependency Analysis
The component selection module depends on several other components within the system, forming a complex interdependent network that enables autonomous signal analysis.

```mermaid
graph TD
select_component[select_component.py] --> numpy[NumPy]
select_component --> matplotlib[Matplotlib]
select_component --> pickle[Pickle]
quantitative_parameterization_module[quantitative_parameterization_module.py] --> scipy[SciPy]
quantitative_parameterization_module --> numpy
quantitative_parameterization_module --> rlowess[rlowess_smoother.py]
LLMOrchestrator[LLMOrchestrator.py] --> genai[Google Generative AI]
LLMOrchestrator --> langchain[LangChain]
LLMOrchestrator --> chroma[Chroma DB]
LLMOrchestrator --> select_component
LLMOrchestrator --> quantitative_parameterization_module
decompose_matrix_nmf[decompose_matrix_nmf.py] --> numpy
decompose_matrix_nmf --> matplotlib
decompose_matrix_nmf --> pickle
decompose_matrix_nmf --> rlowess
select_component -.-> quantitative_parameterization_module
decompose_matrix_nmf -.-> quantitative_parameterization_module
```

**Diagram sources**
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [quantitative_parameterization_module.py](file://src/core/quantitative_parameterization_module.py#L1-L1075)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)
- [decompose_matrix_nmf.py](file://src/tools/decomposition/decompose_matrix_nmf.py#L1-L195)

## Performance Considerations
The component selection process is computationally lightweight compared to the NMF decomposition itself. The selection operation involves simple array indexing and basic plotting, making it efficient for real-time analysis. However, the overall performance of the autonomous analysis pipeline depends on the LLM response time and the computational cost of preceding decomposition steps.

The system employs several optimization strategies:
- Caching of intermediate results using pickle serialization
- Efficient memory management through NumPy arrays
- Asynchronous execution of pipeline steps
- Pre-computed vector stores for rapid retrieval of tool documentation

## Troubleshooting Guide
Common issues and their solutions when using the component selection module:

**Section sources**
- [select_component.py](file://src/tools/decomposition/select_component.py#L1-L113)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)

### Component Index Out of Bounds
**Issue**: IndexError when selecting a component index that exceeds available components
**Solution**: Verify the number of components from the NMF decomposition before selection. Use the quantitative parameterization module to inspect the decomposition results first.

### Missing Input Data
**Issue**: KeyError when required data keys are missing from input dictionary
**Solution**: Ensure the input dictionary contains 'new_params' with 'signals_reconstructed' and 'sampling_rate' keys. Validate the output of the preceding decomposition step.

### LLM Not Selecting Components
**Issue**: The LLM orchestrator fails to propose component selection after decomposition
**Solution**: Check the evaluation criteria in the LLM prompt. Ensure the quantitative metrics are being computed and available for the LLM to assess component relevance.

### Visualization Issues
**Issue**: Component visualization not saving correctly
**Solution**: Verify the output directory exists and is writable. Check file paths for invalid characters. Ensure matplotlib is properly configured.

## Conclusion
The component selection module plays a crucial role in the autonomous signal analysis system by enabling focused examination of specific components identified through NMF decomposition. Integrated with quantitative parameterization and LLM-based decision making, it forms part of a sophisticated pipeline for fault diagnosis in mechanical systems. The modular design allows for easy extension and adaptation to different signal processing workflows and diagnostic requirements.