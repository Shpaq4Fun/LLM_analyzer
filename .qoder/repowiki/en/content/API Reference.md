# API Reference

<cite>
**Referenced Files in This Document**   
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725) - *Updated in recent commit*
- [ContextManager.py](file://src/core/ContextManager.py#L1-L44) - *Added in recent commit*
- [prompt_assembler.py](file://src/core/prompt_assembler.py#L1-L178) - *Updated in recent commit*
- [rag_builder.py](file://src/core/rag_builder.py#L1-L115)
- [API_REFERENCE.md](file://src/docs/API_REFERENCE.md#L1-L96)
- [TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md#L1-L28)
</cite>

## Update Summary
**Changes Made**   
- Added comprehensive documentation for the new ContextManager class
- Updated LLMOrchestrator initialization to reflect integration with ContextManager
- Enhanced ContextManager section with implementation details from source code
- Updated prompt_assembler.py references to reflect context-aware operations
- Added section sources for all analyzed files with update annotations

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [LLMOrchestrator Class](#llmorchestrator-class)
4. [ContextManager Class](#contextmanager-class)
5. [PromptAssembler Class](#promptassembler-class)
6. [RAGBuilder Class](#ragbuilder-class)
7. [Tool Registry and External Tools](#tool-registry-and-external-tools)
8. [Initialization and State Management](#initialization-and-state-management)
9. [Event Hooks and Callbacks](#event-hooks-and-callbacks)
10. [Versioning and Compatibility](#versioning-and-compatibility)
11. [Client Integration Examples](#client-integration-examples)

## Introduction
The AIDA (AI-Driven Analyzer) system provides an autonomous pipeline for data analysis using Large Language Models (LLMs). This API documentation details the core modules responsible for orchestrating analysis workflows, managing context, assembling prompts, and building retrieval-augmented generation (RAG) knowledge bases. The system enables users to define analysis objectives in natural language, after which the LLM autonomously designs and executes a sequence of analytical steps using registered tools.

**Section sources**
- [README.md](file://README.md#L1-L244)

## Core Components

This section details the four primary modules that form the core of the AIDA system: `LLMOrchestrator`, `ContextManager`, `prompt_assembler`, and `rag_builder`. These components work together to manage the analysis lifecycle, maintain conversational and semantic context, construct LLM prompts, and provide domain-specific knowledge via RAG.

**Section sources**
- [API_REFERENCE.md](file://src/docs/API_REFERENCE.md#L1-L96)

## LLMOrchestrator Class

The `LLMOrchestrator` class is the central decision-making engine of the AIDA system. It coordinates the end-to-end autonomous analysis pipeline by communicating with the LLM, managing action sequences, executing generated scripts, and evaluating results iteratively.

### Class Definition
```python
class LLMOrchestrator:
    def __init__(self, user_data_description, user_objective, run_id, loaded_data, signal_var_name, fs_var_name, log_queue):
```

### Initialization Parameters
- **user_data_description**: `str` - Natural language description of the input data provided by the user
- **user_analysis_objective**: `str` - Natural language description of the desired analysis goal
- **run_id**: `str` - Unique identifier for the current analysis session
- **loaded_data**: `dict` - Dictionary containing loaded signal data and sampling rate
- **signal_var_name**: `str` - Key name in `loaded_data` for the signal array
- **fs_var_name**: `str` - Key name in `loaded_data` for the sampling frequency
- **log_queue**: `queue.Queue` - Thread-safe queue for logging messages and GUI updates

### Public Methods

#### run_analysis_pipeline()
Executes the complete autonomous analysis workflow.

**Parameters**: None  
**Returns**: None  
**Exceptions**: Raises exceptions on LLM API errors, script execution failures, or timeouts  
**Thread Safety**: Not thread-safe; designed for single-threaded execution per analysis session  
**State Dependencies**: Depends on initialized `context_manager`, `prompt_assembler`, and valid `loaded_data`

```python
orchestrator = LLMOrchestrator(user_data_description="Vibration signal from bearing", 
                              user_objective="Detect inner race fault", 
                              run_id="run_20250829_090008",
                              loaded_data={"signal": signal_data, "fs": 10000},
                              signal_var_name="signal",
                              fs_var_name="fs",
                              log_queue=log_queue)
orchestrator.run_analysis_pipeline()
```

### Private Methods

#### _create_metaknowledge()
Generates structured metadata about the dataset by querying the LLM with RAG-enhanced context.

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L85-L145)

#### _fetch_next_action(evaluation)
Determines the next analytical step based on the evaluation of the previous result.

**Parameters**: 
- **evaluation**: `str` - JSON string containing evaluation results from `_evaluate_result`

**Returns**: `dict` representing the next action with keys: `action_id`, `tool_name`, `params`, `output_variable`

#### _execute_current_pipeline()
Translates the current sequence of actions into executable Python code and runs it in a subprocess.

**Returns**: `dict` with keys:
- **data**: Result dictionary from the executed script
- **image_path**: Path to the generated visualization (if any)

**Execution Environment**: Runs in isolated subprocess with timeout of 1500 seconds

#### _evaluate_result(result, action_taken)
Asks the LLM to assess the usefulness of the latest analysis result and determine whether to continue or terminate.

**Parameters**:
- **result**: `dict` - Output from `_execute_current_pipeline`
- **action_taken**: `dict` - The action that produced the result

**Returns**: JSON string with evaluation containing:
- **is_useful**: `bool` - Whether the result advances the analysis
- **is_final**: `bool` - Whether the analysis objective has been achieved
- **tool_name**: `str` - Suggested next tool to use
- **input_variable**: `str` - Variable to use as input for next step
- **params**: `dict` - Parameters for the next action
- **justification**: `str` - Explanation of the evaluation

#### _translate_actions_to_code()
Converts the list of action objects into a complete Python script.

**Returns**: `str` containing executable Python code with proper imports, variable handling, and tool calls

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L147-L725)

## ContextManager Class

Manages the conversational and semantic context throughout the analysis session. The ContextManager class was recently implemented to provide persistent context management for the LLM orchestrator, enabling more coherent and context-aware interactions.

### Class Definition
```python
class ContextManager:
    def __init__(self):
```

### Attributes
- **conversation_history**: `list` - Complete history of LLM interactions with timestamps and metadata
- **semantic_memory**: `dict` - Learned patterns and domain knowledge accumulated during analysis
- **episodic_memory**: `list` - Time-ordered events of the analysis session
- **working_memory**: `list` - Current session state and temporary information
- **variable_registry**: `dict` - Current state of variables and their values
- **max_context_length**: `int` - Maximum number of interactions to retain (50,000)

### Methods

#### add_interaction(prompt, response, metadata)
Records an interaction between the system and the LLM, preserving the conversation history.

**Parameters**:
- **prompt**: `str` - The prompt sent to the LLM
- **response**: `str` - The response received from the LLM
- **metadata**: `dict` - Additional context including run_id, step_number, model_name, timestamp

**Implementation Details**: Creates a history entry with timestamp, step number, interaction type, prompt, response, and metadata, then appends it to conversation_history.

#### build_context(context_type, current_task)
Constructs the contextual prompt for the LLM by formatting the conversation history and prepending it to the current task.

**Parameters**:
- **context_type**: `str` - Type of context ("analysis", "metaknowledge", "evaluation")
- **current_task**: `str` - The current task prompt

**Returns**: `str` - Complete prompt with context header, formatted history, and current task

**Implementation Details**: Formats the conversation history into a readable string and returns it with the current task, separated by context markers.

#### _format_context(conversation_history)
Formats the conversation history into a human-readable string format for inclusion in prompts.

**Returns**: `str` - Formatted conversation history with timestamps, prompts, and responses

**Implementation Details**: Iterates through conversation history entries and formats them with timestamps, prompts, responses, and separators.

**Section sources**
- [ContextManager.py](file://src/core/ContextManager.py#L1-L44) - *Added in recent commit*
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L25-L725) - *Updated to use ContextManager*

## PromptAssembler Class

Responsible for constructing the final prompts sent to the LLM by combining templates with dynamic context.

### Class Definition
```python
class PromptAssembler:
    def __init__(self):
```

### Methods

#### build_prompt(prompt_type, context_bundle)
Main entry point for prompt construction.

**Parameters**:
- **prompt_type**: `str` - Type of prompt to build ("METAKNOWLEDGE_CONSTRUCTION", "EVALUATE_LOCAL_CRITERION")
- **context_bundle**: `dict` - Collection of all necessary context for prompt assembly

**Returns**: `str` or `list` - Final prompt, potentially including image objects for multimodal processing

#### _build_metaknowledge_prompt(context_bundle)
Creates the prompt for generating structured metaknowledge about the dataset.

**context_bundle** must contain:
- **raw_signal_data**: `np.ndarray` - The actual signal data
- **sampling_frequency**: `int` - Sampling rate in Hz
- **user_data_description**: `str` - User's description of the data
- **user_analysis_objective**: `str` - User's analysis goal
- **rag_retriever**: `Chroma.as_retriever()` - Knowledge base retriever
- **rag_retriever_tools**: `Chroma.as_retriever()` - Tool documentation retriever
- **tools_list**: `str` - Content of TOOLS_REFERENCE.md

#### _build_evaluate_local_prompt(context_bundle)
Creates the prompt for evaluating the results of an analysis step.

**context_bundle** must contain:
- **metaknowledge**: `dict` - Structured knowledge about the dataset
- **last_action**: `dict` - The most recently executed action
- **last_result**: `dict` - Output from the last action
- **sequence_steps**: `list` - Complete pipeline of actions so far
- **rag_retriever**: `Chroma.as_retriever()` - Knowledge base retriever
- **rag_retriever_tools**: `Chroma.as_retriever()` - Tool documentation retriever
- **tools_list**: `str` - Content of TOOLS_REFERENCE.md
- **user_data_description**: `str` - User's description of the data
- **user_analysis_objective**: `str` - User's analysis goal
- **result_history**: `list` - History of all previous results

**Returns**: `list` containing the prompt string followed by PIL.Image objects for visual evaluation

#### _load_prompt_templates()
Loads all text templates from the `src/prompt_templates/` directory into a dictionary.

**Section sources**
- [prompt_assembler.py](file://src/core/prompt_assembler.py#L1-L178) - *Updated to work with ContextManager*

## RAGBuilder Class

Constructs and loads vector-based knowledge retrieval systems using ChromaDB and LangChain.

### Class Definition
```python
class RAGBuilder:
    def __init__(self):
```

### Methods

#### build_index(knowledge_base_paths, queue, persist_directory, embedding_model)
Creates a persistent vector store from documents in specified directories.

**Parameters**:
- **knowledge_base_paths**: `list[str]` - List of directories containing knowledge documents
- **queue**: `queue.Queue` - For progress updates to GUI
- **persist_directory**: `str` - Directory to save the vector store
- **embedding_model**: `str` - Name of the HuggingFace embedding model (default: "all-MiniLM-L12-v2")

**Supported Document Types**: `.md`, `.py`, `.pdf` files

**Processing Steps**:
1. Load documents from specified paths
2. Split documents into chunks (800 characters, 500 overlap)
3. Generate embeddings using sentence-transformers
4. Create and persist ChromaDB vector store

**Returns**: `Chroma` vector store object

**Event Hooks**: Sends progress messages to the provided queue with format: `("log", {"sender": "RAGBuilder", "message": message})`

#### load_index(persist_directory)
Loads a previously built vector store from disk.

**Parameters**:
- **persist_directory**: `str` - Directory where the index is stored

**Returns**: `Chroma` vector store object

**Exceptions**: Raises `FileNotFoundError` if the directory does not exist

**Section sources**
- [rag_builder.py](file://src/core/rag_builder.py#L1-L115)

## Tool Registry and External Tools

The AIDA system uses a modular tool registry pattern where analytical functions are discovered and invoked dynamically.

### Tool Categories

#### utils
- **load_data**: Loads signal data and sampling rate, generates initial visualization

#### sigproc
- **lowpass_filter**: Removes high-frequency noise
- **highpass_filter**: Removes low-frequency drift
- **bandpass_filter**: Isolates specific frequency ranges

#### transforms
- **create_fft_spectrum**: Frequency domain analysis
- **create_envelope_spectrum**: Amplitude modulation detection
- **create_signal_spectrogram**: Time-frequency representation
- **create_csc_map**: Cyclostationary coherence analysis

#### decomposition
- **decompose_matrix_nmf**: Non-negative matrix factorization
- **select_component**: Extracts specific signal components

### Tool Invocation Process
1. LLM selects tool name and parameters via `_fetch_next_action`
2. `_translate_actions_to_code` generates import statements based on tool name
3. Generated script imports the tool function directly: `from src.tools.{category}.{tool_name} import {tool_name}`
4. Script executes the tool with provided parameters
5. Results are parameterized using `calculate_quantitative_metrics`

**Section sources**
- [TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md#L1-L28)

## Initialization and State Management

The system manages state through a combination of in-memory objects and disk persistence.

### Run State Directory
Created at `./run_state/{run_id}` with the following files:
- `metaknowledge.json`: Structured metadata about the dataset
- `signal_data_{run_id}.pkl`: Pickled signal data
- `sampling_rate_{run_id}.pkl`: Pickled sampling rate
- `current_result_{run_id}.pkl`: Latest analysis results
- `step_*.png`: Visualizations from each pipeline step
- Temporary Python scripts for pipeline execution

### State Dependencies
- `LLMOrchestrator` depends on successful initialization of `ContextManager` and `PromptAssembler`
- `PromptAssembler` requires all template files to be present in `src/prompt_templates/`
- `RAGBuilder` requires document files in the knowledge base directories
- All components assume the vector stores exist at `./vector_store` and `./vector_store_tools`

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L25-L725)

## Event Hooks and Callbacks

The system uses a queue-based event system for communication between components and the GUI.

### Message Types
- **log**: Text messages for logging and display
  - Format: `("log", {"sender": str, "message": str})`
- **flowchart_add_step**: Add a step to the GUI flowchart
  - Format: `("flowchart_add_step", {"action_id": int, "tool_name": str, "output_variable": str, "image_path": str})`
- **image_display**: Display an image in the GUI
  - Format: `("image_display", {"image_path": str})`
- **finish**: Analysis completed successfully
  - Format: `("finish", None)`
- **error**: Error occurred during processing
  - Format: `("error", str)`

### Callback Integration
Components send messages to the `log_queue` provided during initialization. The GUI's `process_queue` method handles these messages to update the interface in real-time.

**Section sources**
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L25-L725)
- [rag_builder.py](file://src/core/rag_builder.py#L1-L115)

## Versioning and Compatibility

### Backward Compatibility
- The system maintains backward compatibility with existing tool interfaces
- Parameter defaults are preserved in tool functions
- The `TOOLS_REFERENCE.md` file serves as a contract for tool signatures
- Prompt templates use named formatting (`{variable}`) for robustness

### Deprecation Policy
- Deprecated tools are marked in documentation but remain functional
- Major version changes may remove deprecated tools
- The `prompt_assembler` uses versioned templates (e.g., `metaknowledge_prompt_v2.txt`)
- Users can extend functionality by adding new tools in appropriate subdirectories

### Version Constraints
- Python 3.8+
- Google Generative AI SDK
- LangChain and ChromaDB for RAG functionality
- Specific embedding models: "all-MiniLM-L12-v2" or compatible HuggingFace models

**Section sources**
- [README.md](file://README.md#L1-L244)
- [API_REFERENCE.md](file://src/docs/API_REFERENCE.md#L1-L96)

## Client Integration Examples

### Basic Integration
```python
import queue
from src.core.LLMOrchestrator import LLMOrchestrator

# Set up communication queue
log_queue = queue.Queue()

# Initialize orchestrator
orchestrator = LLMOrchestrator(
    user_data_description="Vibration signal from industrial bearing",
    user_objective="Detect early signs of inner race fault",
    run_id="analysis_001",
    loaded_data={"vibration": signal_array, "sampling_rate": 10000},
    signal_var_name="vibration",
    fs_var_name="sampling_rate",
    log_queue=log_queue
)

# Start autonomous analysis
orchestrator.run_analysis_pipeline()

# Process results
while not log_queue.empty():
    message_type, content = log_queue.get()
    if message_type == "log":
        print(f"[{content['sender']}] {content['message']}")
    elif message_type == "image_display":
        display_image(content['image_path'])
```

### RAG Index Management
```python
from src.core.rag_builder import RAGBuilder
import queue

# Build knowledge base
rag_queue = queue.Queue()
rag_builder = RAGBuilder()
rag_builder.build_index(
    knowledge_base_paths=["knowledge_base"],
    queue=rag_queue,
    persist_directory="./vector_store"
)

# Monitor progress
while True:
    try:
        msg_type, content = rag_queue.get(timeout=1)
        if msg_type == "finish":
            break
        elif msg_type == "log":
            print(content["message"])
    except queue.Empty:
        continue
```

### Custom Tool Integration
To add a new tool, create a Python file in the appropriate tools subdirectory:

```python
# src/tools/transforms/custom_analysis.py
def custom_analysis(data: dict, output_image_path: str, parameter: float = 1.0) -> dict:
    """
    Perform custom analysis on the input data.
    
    Args:
        data: Input data dictionary with 'signal_data' and 'sampling_rate'
        output_image_path: Path to save the visualization
        parameter: Custom parameter for the analysis
    
    Returns:
        Dictionary containing:
        - 'result': Analysis result
        - 'image_path': Path to saved plot
        - 'metrics': Quantitative metrics
    """
    # Implementation here
    pass
```

Update `TOOLS_REFERENCE.md` to include the new tool, and it will be automatically available to the LLM orchestrator.

**Section sources**
- [README.md](file://README.md#L1-L244)
- [API_REFERENCE.md](file://src/docs/API_REFERENCE.md#L1-L96)
- [LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L1-L725)