# AIDA - AI-Driven Analyzer

**Autonomous LLM-Orchestrated Data Analysis Pipeline**

AIDA is an intelligent data analysis system that autonomously designs and executes data processing pipelines using Large Language Models (LLMs). Instead of manual tool selection and parameter tuning, AIDA leverages AI to iteratively plan, execute, and evaluate analysis steps to achieve user-defined objectives.

![System Architecture](./architecture.png)

## 🎯 Key Features

- **Autonomous Analysis**: LLM-driven pipeline orchestration with minimal human intervention
- **Multimodal Intelligence**: Visual analysis of results using Google Gemini's multimodal capabilities
- **RAG-Enhanced**: Retrieval-Augmented Generation with domain-specific knowledge base
- **Modular Tools**: Extensible toolkit for signal processing, transforms, and decomposition
- **Interactive GUI**: User-friendly interface built with CustomTkinter
- **Real-time Feedback**: Visual and quantitative evaluation of analysis results

## 🏗️ System Architecture

AIDA consists of several key components:

- **LLM Orchestrator**: Central decision-making engine using Google Gemini
- **RAG System**: Vector-based knowledge retrieval using ChromaDB and LangChain
- **Tool Registry**: Modular analysis tools organized by category
- **Code Translator**: Converts action sequences to executable Python scripts
- **GUI Interface**: Interactive frontend for data loading and analysis monitoring
- **Knowledge Base**: Curated domain expertise and documentation

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
│   │   ├── LLMOrchestrator.py # Main orchestration logic
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

## 📖 Documentation

- [API Reference](src/docs/API_REFERENCE.md) - Complete API documentation
- [Tools Reference](src/docs/TOOLS_REFERENCE.md) - Available analysis tools
- [Concept Document](concept.md) - Detailed system design and architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔧 Technical Details

### LLM Integration
- **Primary Model**: Google Gemini 2.5 Pro/Flash
- **Context Window**: Up to 1 million tokens
- **Multimodal**: Supports text and image analysis
- **Fallback Models**: Automatic fallback to alternative Gemini versions

### RAG System
- **Embedding Model**: HuggingFace all-MiniLM-L12-v2
- **Vector Store**: ChromaDB with persistent storage
- **Knowledge Sources**: Scientific papers, tool documentation, domain rules
- **Retrieval**: Top-k similarity search with configurable parameters

### Pipeline Execution
- **Code Generation**: Dynamic Python script creation
- **Subprocess Execution**: Isolated execution environment
- **State Management**: Persistent state across pipeline steps
- **Error Handling**: Robust error recovery and logging

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
- **Memory Usage**: ~500MB-2GB depending on data size
- **Token Consumption**: ~10K-50K tokens per analysis
- **Supported Data**: Up to 1M samples per signal

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
