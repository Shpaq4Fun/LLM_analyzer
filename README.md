# AIDA - AI Driven Analyzer

**Autonomous LLM-Orchestrated Data Analysis Pipeline**

AIDA is an intelligent data analysis system that autonomously designs and executes data processing pipelines using Large Language Models (LLMs). Instead of manual tool selection and parameter tuning, AIDA leverages AI to iteratively plan, execute, and evaluate analysis steps to achieve user-defined objectives.

![System Architecture](./architecture.png)

![Screenshot](./3.png)

## 🎯 Key Features 

- **Autonomous Analysis**: LLM-driven pipeline orchestration with minimal human intervention
- **Persistent Context Management**: Conversation history and learning capabilities for improved analysis consistency
- **Multimodal Intelligence**: Visual analysis of results using Google Gemini's multimodal capabilities
- **RAG-Enhanced**: Retrieval-Augmented Generation with domain-specific knowledge base
- **Modular Tools**: Extensible toolkit for signal processing, transforms, and decomposition
- **Interactive GUI**: User-friendly interface built with CustomTkinter
- **Real-time Feedback**: Visual and quantitative evaluation of analysis results
- **Iterative Learning**: System learns from previous analysis steps to improve consistency and decision-making

## 🏗️ System Architecture

AIDA consists of several key components:

- **LLM Orchestrator**: Central decision-making engine using Google Gemini with context management
- **Context Manager**: Persistent conversation history and learning capabilities for improved analysis consistency
- **RAG System**: Vector-based knowledge retrieval using ChromaDB and LangChain
- **Tool Registry**: Modular analysis tools organized by category
- **Code Translator**: Converts action sequences to executable Python scripts
- **GUI Interface**: Interactive frontend for data loading and analysis monitoring
- **Knowledge Base**: Curated domain expertise and documentation

## 🆕 What's New

### Recent Updates (Latest Commit)

🎆 **Persistent Context Management Implementation**
- Added `ContextManager` class for conversation history and state management
- Enhanced `LLMOrchestrator` with context-aware LLM interactions
- Improved analysis consistency through variable registry and context tracking
- Foundation laid for future learning and adaptation capabilities
- Context size management with configurable limits
- Metadata tracking for better error recovery and debugging

These changes transform AIDA from a stateless tool into an intelligent system that maintains memory across analysis steps, leading to more consistent and context-aware data analysis.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API access
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LLM_analyzer.git
   cd LLM_analyzer
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure authentication**
   - Set up Google Gemini API credentials
   - Follow the authentication setup in `src/core/authentication.py`

5. **Build knowledge base (optional)**
   ```bash
   python -c "from src.core.rag_builder import RAGBuilder; RAGBuilder().build_index(['knowledge_base'], None, './vector_store')"
   ```

### Running AIDA

```bash
python src/app.py
```

## 📊 Usage

1. **Load Data**: Import your time-series data (CSV, HDF5, etc.)
2. **Set Objective**: Describe your analysis goal in natural language
3. **Start Analysis**: Let AIDA autonomously design and execute the pipeline
4. **Review Results**: Examine generated visualizations and quantitative metrics
5. **Export Script**: Get the complete, executable analysis script

### Example Analysis Objectives

- "Detect bearing faults in vibration signals"
- "Identify periodic components in the time series"
- "Perform spectral analysis to find dominant frequencies"
- "Decompose signal into meaningful components"

## 🛠️ Available Tools

### Signal Processing (`src/tools/sigproc/`)
- **Lowpass Filter**: Remove high-frequency noise
- **Highpass Filter**: Remove low-frequency drift
- **Bandpass Filter**: Isolate specific frequency ranges

### Transforms (`src/tools/transforms/`)
- **FFT Spectrum**: Frequency domain analysis
- **Envelope Spectrum**: Amplitude modulation detection
- **Spectrogram**: Time-frequency representation
- **CSC Map**: Cyclostationary coherence analysis

### Decomposition (`src/tools/decomposition/`)
- **NMF Decomposition**: Non-negative matrix factorization
- **Component Selection**: Extract specific signal components

### Utilities (`src/tools/utils/`)
- **Data Loader**: Import and preprocess various data formats

## 📁 Project Structure

```
LLM_analyzer/
├── src/
│   ├── app.py                 # Application entry point
│   ├── core/                  # Core system components
│   │   ├── LLMOrchestrator.py # Main orchestration logic with context management
│   │   ├── ContextManager.py  # Persistent context and conversation history
│   │   ├── prompt_assembler.py # Prompt construction
│   │   ├── rag_builder.py     # Knowledge base indexing
│   │   └── authentication.py  # API authentication
│   ├── gui/                   # User interface
│   │   └── main_window.py     # Main GUI application
│   ├── tools/                 # Analysis tools
│   │   ├── sigproc/          # Signal processing
│   │   ├── transforms/       # Transform operations
│   │   ├── decomposition/    # Signal decomposition
│   │   └── utils/            # Utility functions
│   ├── docs/                  # Documentation
│   └── prompt_templates/      # LLM prompt templates
├── knowledge_base/            # Domain expertise documents
├── vector_store/             # RAG vector database
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (if not using CLI auth)

### Customization
- **Add Tools**: Create new analysis tools in `src/tools/`
- **Extend Knowledge**: Add domain documents to `knowledge_base/`
- **Modify Prompts**: Edit templates in `src/prompt_templates/`

## 🧠 Persistent Context Management

**NEW FEATURE**: AIDA now includes advanced persistent context management that enhances analysis consistency and enables learning from previous interactions.

### Key Capabilities

- **Conversation History**: Maintains a complete record of all LLM interactions within a session
- **Variable Registry**: Tracks variable states and naming consistency across pipeline steps
- **Contextual Prompts**: Injects relevant conversation history into LLM prompts
- **Learning Foundation**: Establishes the groundwork for pattern recognition and iterative improvement
- **Error Context**: Provides context-aware error recovery and debugging

### Benefits

- **Improved Consistency**: Maintains variable naming and analysis approaches across iterations
- **Better Error Recovery**: Understands failure context to apply appropriate corrections
- **Progressive Analysis**: Builds upon previous understanding rather than starting fresh
- **Enhanced Decision Making**: Makes informed choices based on conversation history
- **Foundation for Learning**: Prepares the system for future learning and adaptation capabilities

### Implementation Details

- **ContextManager**: New core component (`src/core/ContextManager.py`) that manages conversation history
- **Enhanced LLMOrchestrator**: Integrated context-aware LLM interactions using `_generate_content_with_context()`
- **Metadata Tracking**: Records interaction types, timestamps, and execution outcomes
- **Context Formatting**: Intelligent context injection that prepends relevant history to prompts
- **Memory Management**: Configurable context size limits (50KB default) to manage token usage

This enhancement transforms AIDA from a stateless analysis tool into an intelligent system that learns and adapts throughout the analysis process.

## 📖 Documentation

- [API Reference](src/docs/API_REFERENCE.md) - Complete API documentation
- [Tools Reference](src/docs/TOOLS_REFERENCE.md) - Available analysis tools
- [Concept Document](concept.md) - Detailed system design and architecture
- [Persistent Context Implementation](PERSISTENT_CONTEXT_IMPLEMENTATION.md) - Detailed implementation plan and technical specifications for the context management system
- [Project Description](PROJECT_DESCRIPTION.md) - Comprehensive project overview and technical analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔧 Technical Details

### LLM Integration
- **Primary Model**: Google Gemini 2.5 Pro/Flash
- **Context Window**: Up to 1 million tokens with persistent conversation history
- **Multimodal**: Supports text and image analysis
- **Fallback Models**: Automatic fallback to alternative Gemini versions
- **Context Management**: Maintains conversation history and learns from previous interactions

### RAG System
- **Embedding Model**: HuggingFace all-MiniLM-L12-v2
- **Vector Store**: ChromaDB with persistent storage
- **Knowledge Sources**: Scientific papers, tool documentation, domain rules
- **Retrieval**: Top-k similarity search with configurable parameters

### Pipeline Execution
- **Code Generation**: Dynamic Python script creation with context awareness
- **Subprocess Execution**: Isolated execution environment
- **State Management**: Persistent state across pipeline steps with conversation history
- **Context-Aware Processing**: Maintains variable naming consistency and learned patterns
- **Error Handling**: Robust error recovery and logging with context-based error analysis

## 🧪 Example Workflow

1. **Data Input**: Load vibration signal data (e.g., bearing monitoring)
2. **Objective Setting**: "Detect inner race bearing fault"
3. **Autonomous Analysis**: LLM orchestrates analysis steps to design a complete pipeline as a Python script
4. **Output**: Complete analysis script + diagnostic results

## 🚨 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Ensure Gemini API is properly configured
export GEMINI_API_KEY="your-api-key"
```

**Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**Vector Store Issues**
```bash
# Rebuild knowledge base
python -c "from src.core.rag_builder import RAGBuilder; RAGBuilder().build_index(['knowledge_base'], None, './vector_store')"
```

**GUI Not Starting**
- Check Python version (3.8+ required)
- Verify CustomTkinter installation
- Ensure display environment is available

## 📊 Performance

- **Analysis Speed**: Typically 2-5 minutes per pipeline
- **Memory Usage**: ~500MB-2GB depending on data size (plus context storage)
- **Token Consumption**: ~10K-50K tokens per analysis (enhanced with conversation context)
- **Supported Data**: Up to 1M samples per signal
- **Context Storage**: Persistent conversation history with 50KB limit per session

## 🔒 Security & Privacy

- **Local Processing**: All data analysis runs locally
- **API Calls**: Only prompts and metadata sent to LLM
- **No Data Upload**: Raw data never leaves your system
- **Secure Storage**: Encrypted credential management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini for multimodal AI capabilities
- LangChain for RAG implementation
- ChromaDB for vector storage
- The open-source community for various Python libraries

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation in `src/docs/`
- Review the concept document for system architecture details

---

**AIDA** - Transforming data analysis through autonomous AI orchestration
