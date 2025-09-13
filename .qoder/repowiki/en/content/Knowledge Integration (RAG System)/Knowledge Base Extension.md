# Knowledge Base Extension

<cite>
**Referenced Files in This Document**   
- [src/docs/TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md)
- [src/core/rag_builder.py](file://src/core/rag_builder.py)
- [src/prompt_templates/metaknowledge_prompt.txt](file://src/prompt_templates/metaknowledge_prompt.txt)
- [src/core/LLMOrchestrator.py](file://src/core/LLMOrchestrator.py)
- [src/core/prompt_assembler.py](file://src/core/prompt_assembler.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Extending the Tool Registry](#extending-the-tool-registry)
3. [Registering Tools in the System](#registering-tools-in-the-system)
4. [Retraining the ChromaDB Index](#retraining-the-chromadb-index)
5. [Customizing Embedding Templates](#customizing-embedding-templates)
6. [Structuring Domain Knowledge for Optimal Retrieval](#structuring-domain-knowledge-for-optimal-retrieval)
7. [Example: Adding a Signal Processing Tool](#example-adding-a-signal-processing-tool)
8. [Versioning and Backward Compatibility](#versioning-and-backward-compatibility)
9. [Validation and Debugging Procedures](#validation-and-debugging-procedures)
10. [Conclusion](#conclusion)

## Introduction
This document provides a comprehensive guide for extending the RAG system's knowledge base with new tools or domains within the AIDA (Autonomous LLM-Orchestrated Data Analysis) framework. It details the process of integrating new analytical capabilities, ensuring they are discoverable and usable by the LLMOrchestrator. The guide covers formatting documentation, registering tools, retraining retrieval indices, customizing analysis templates, and validating integrations. The goal is to maintain system coherence while enabling flexible expansion of analytical functionality.

## Extending the Tool Registry

To extend the system with new analytical tools, follow a structured approach that ensures compatibility with the LLMOrchestrator and RAG retrieval system. The process begins with proper documentation in the TOOLS_REFERENCE.md file, which serves as the primary source of truth for tool discovery.

The TOOLS_REFERENCE.md file uses a hierarchical structure organized by tool categories (e.g., `utils`, `sigproc`, `transforms`, `decomposition`). Each tool entry includes the file path and function signature with type annotations. This standardized format enables the LLMOrchestrator to parse tool capabilities and generate appropriate usage code.

When adding a new tool:
1. Choose an appropriate category directory under `src/tools/`
2. Create both `.py` (implementation) and `.md` (documentation) files
3. Document the function signature in TOOLS_REFERENCE.md using the established format
4. Ensure type hints are included in the Python function definition

The system relies on this documentation for tool discovery and parameter inference, making accurate and complete entries essential for proper integration.

**Section sources**
- [src/docs/TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md)

## Registering Tools in the System

Tool registration occurs automatically through file system organization and documentation parsing. The LLMOrchestrator loads tool information from TOOLS_REFERENCE.md during initialization via the `_get_available_tools()` method.

```python
def _get_available_tools(self, tools_reference_path='src/docs/TOOLS_REFERENCE.md'):
    """
    Loads the content of the TOOLS_REFERENCE.md file for better API description.
    """
    try:
        with open(tools_reference_path, 'r', encoding='utf-8') as f:
            tools_reference_content = f.read()
        return tools_reference_content
    except FileNotFoundError:
        return "Tools reference file not found."
    except Exception as e:
        return f"Error loading tools reference: {str(e)}"
```

This method reads the entire TOOLS_REFERENCE.md file and makes its content available to the LLM context. The orchestrator uses this information to understand available tools, their parameters, and expected inputs/outputs.

For proper registration:
- Maintain consistent naming between file names and function names
- Use clear, descriptive parameter names
- Include default values where appropriate
- Ensure the tool directory structure matches the category in TOOLS_REFERENCE.md

The system automatically detects tools based on their presence in the reference file and their location in the appropriate subdirectory.

**Section sources**
- [src/core/LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L700-L715)

## Retraining the ChromaDB Index

After adding new tools or domain knowledge, the ChromaDB vector index must be rebuilt to incorporate the updated information. The RAGBuilder class handles index creation and persistence.

```python
class RAGBuilder:
    def build_index(self, knowledge_base_paths, queue, persist_directory, embedding_model="all-MiniLM-L12-v2"):
        """
        Builds the RAG index from the specified knowledge base paths.
        Accepts a list of paths to index.
        Uses a queue to send progress updates back to the main thread.
        """
```

To retrain the index:
1. Ensure new documentation files (.md, .py, .pdf) are placed in indexed directories
2. Call `RAGBuilder().build_index()` with appropriate parameters
3. Specify the persistence directory (typically `./vector_store`)
4. Monitor progress through the provided queue

The indexing process:
- Loads documents from specified paths
- Splits content into 800-character chunks with 500-character overlap
- Generates embeddings using the HuggingFace all-MiniLM-L12-v2 model
- Persists the vector store for future retrieval

After retraining, restart the application to ensure the LLMOrchestrator loads the updated index.

**Section sources**
- [src/core/rag_builder.py](file://src/core/rag_builder.py#L20-L115)

## Customizing Embedding Templates

The metaknowledge_prompt.txt template defines how user objectives and data descriptions are converted into structured JSON for analysis planning. Customizing this template enables support for new analysis types and domain-specific reasoning.

```text
Your current task is to parse the user's description and objective, along with provided context, and convert this information into a single, structured JSON object.

Adhere strictly to the following JSON schema:
```json
{
  "data_summary": {
    "type": "string",
    "domain": "string",
    "sampling_frequency_hz": "integer",
    "signal_length_sec": "float",
    "properties": ["string"]
  },
  "system_context": {
    "type": "string",
    "configuration": "string",
    "characteristic_frequencies": {
      "bpfi_ratio": "float or null",
      "bpfo_ratio": "float or null",
      "ftf_ratio": "float or null",
      "bsf_ratio": "float or null",
      "unknown_fault_frequency_hz": "float or null"
    }
  },
  "analysis_objective": {
    "primary_goal": "string",
    "target_fault_type": "string or null",
    "target_signal_feature": "string",
    "fallback_goal": "string or null"
  },
  "initial_hypotheses": ["string"]
}
```
```

To customize for new domains:
1. Modify the JSON schema to include domain-specific fields
2. Update validation logic in the LLMOrchestrator's `_create_metaknowledge()` method
3. Adjust the prompt to guide extraction of new parameters
4. Ensure backward compatibility by making new fields optional

The template uses placeholders (`{ground_truth_summary}`, `{rag_context}`, `{user_data_description}`, etc.) that are populated at runtime from various sources, including RAG retrieval results.

**Section sources**
- [src/prompt_templates/metaknowledge_prompt.txt](file://src/prompt_templates/metaknowledge_prompt.txt#L1-L60)

## Structuring Domain Knowledge for Optimal Retrieval

Effective knowledge structuring maximizes retrieval effectiveness by aligning document organization with expected query patterns. The system uses semantic similarity search to retrieve relevant context, so document structure directly impacts performance.

Best practices for knowledge structuring:
- **Granularity**: Keep documents focused on single topics or tools
- **Redundancy**: Include key information in multiple related documents
- **Cross-linking**: Reference related tools and concepts within documentation
- **Standardization**: Use consistent terminology across documents
- **Hierarchy**: Organize by functional categories that match analysis workflows

The RAG system indexes .md, .py, and .pdf files from specified directories. Documentation should be placed in directories that are included in the knowledge_base_paths parameter during index building.

For optimal retrieval:
- Place tool-specific documentation in the same directory as the tool implementation
- Use descriptive file names that match likely search terms
- Include both technical specifications and usage examples
- Document edge cases and limitations

The text splitter uses 800-character chunks with 500-character overlap, so important concepts should be contained within this window when possible.

**Section sources**
- [src/core/rag_builder.py](file://src/core/rag_builder.py#L50-L60)

## Example: Adding a Signal Processing Tool

This example demonstrates adding a new signal processing tool called `notch_filter` to remove specific frequency interference.

**Step 1: Create Implementation File**
Create `src/tools/sigproc/notch_filter.py`:
```python
def notch_filter(data: dict, output_image_path: str, center_freq: float = 1800, quality_factor: int = 30) -> dict:
    """
    Apply a notch filter to remove narrowband interference.
    
    Args:
        data: Dictionary containing signal data
        output_image_path: Path to save visualization
        center_freq: Frequency to remove (Hz)
        quality_factor: Quality factor of the filter
    
    Returns:
        Dictionary with filtered signal and metadata
    """
    # Implementation here
    pass
```

**Step 2: Create Documentation**
Create `src/tools/sigproc/notch_filter.md` with usage examples and theory.

**Step 3: Register in TOOLS_REFERENCE.md**
Add to the sigproc section:
```
### sigproc
- src/tools/sigproc/notch_filter.py
  - notch_filter(data: dict, output_image_path: str, center_freq: float = 1800, quality_factor: int = 30) -> dict
```

**Step 4: Update Tool Submodule Map**
In LLMOrchestrator._translate_actions_to_code(), ensure sigproc is mapped:
```python
tool_submodule_map = {
    # ... existing tools
    "notch_filter": "sigproc"
}
```

**Step 5: Retrain Index**
```python
from src.core.rag_builder import RAGBuilder
RAGBuilder().build_index(['knowledge_base', 'src'], None, './vector_store')
```

**Step 6: Verify Discovery**
The LLMOrchestrator will now include notch_filter in its tool list and can propose it when narrowband interference removal is relevant to the analysis objective.

**Section sources**
- [src/docs/TOOLS_REFERENCE.md](file://src/docs/TOOLS_REFERENCE.md)
- [src/core/LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L550-L570)

## Versioning and Backward Compatibility

The system handles versioning through multiple mechanisms to ensure backward compatibility while supporting evolution.

**File-based Versioning**
- Prompt templates use versioned files (e.g., `meta_template_prompt_v2.txt`)
- The prompt_assembler selects appropriate versions based on configuration
- Old versions are retained for compatibility with existing workflows

**Parameter Compatibility**
- Function parameters should maintain backward compatibility
- New parameters should have sensible defaults
- Deprecated parameters should be handled gracefully
- The LLMOrchestrator uses string similarity (SequenceMatcher) to match parameter names

```python
ratio = SequenceMatcher(None, key, key_orig).ratio()
if ratio > accept_ratio:
    action['params'][key_orig] = params[key]
```

**Index Management**
- Multiple vector stores can coexist (e.g., `vector_store`, `vector_store_tools`)
- The system can load different indices for different knowledge domains
- Index rebuilding does not affect existing analysis runs

When introducing breaking changes:
1. Create new versioned files
2. Update documentation to specify version requirements
3. Implement migration logic in the orchestrator
4. Deprecate old versions gradually

**Section sources**
- [src/core/LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L400-L410)

## Validation and Debugging Procedures

Thorough validation ensures successful integration of new tools and knowledge.

**Integration Verification Steps**
1. Check TOOLS_REFERENCE.md parsing:
```python
# In LLMOrchestrator initialization
self.tools_reference = self._get_available_tools()
self.log_queue.put(("log", {"sender": "System", "message": f"--- TOOLS REFERENCE LOADED ---\n\n {tools_reference_path} \n"}))
```

2. Verify index contents:
- Confirm new documents appear in the loaded document list
- Check chunk count increased appropriately
- Validate embedding generation completes without errors

3. Test tool discovery:
- Set an analysis objective that should trigger the new tool
- Monitor LLM reasoning to see if the tool is considered
- Check the generated script for correct tool import and usage

**Debugging Techniques**
- Enable detailed logging through the log_queue
- Inspect generated scripts in temporary files
- Examine metaknowledge.json for proper parameter extraction
- Review evaluation history for reasoning patterns
- Check vector store persistence directory contents

**Common Issues and Solutions**
- **Tool not discovered**: Verify TOOLS_REFERENCE.md formatting and file paths
- **Parameter mismatch**: Check parameter name similarity and defaults
- **Import errors**: Confirm tool_submodule_map includes the new tool
- **Index not updated**: Rebuild the vector store and restart the application
- **Performance issues**: Optimize document chunking and retrieval parameters

**Section sources**
- [src/core/LLMOrchestrator.py](file://src/core/LLMOrchestrator.py#L200-L250)
- [src/core/rag_builder.py](file://src/core/rag_builder.py#L30-L40)

## Conclusion
Extending the RAG system's knowledge base requires careful attention to documentation standards, registration processes, and validation procedures. By following the structured approach outlined in this guide—properly formatting tool documentation, registering tools in the system, retraining the ChromaDB index, and customizing embedding templates—developers can seamlessly integrate new analytical capabilities. The example of adding a signal processing tool demonstrates the practical application of these principles. Maintaining versioning discipline and conducting thorough validation ensures backward compatibility and system reliability. These extension mechanisms enable the AIDA framework to evolve with new domains and tools while preserving its core autonomous analysis capabilities.