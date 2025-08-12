"""
RAGBuilder constructs and loads Chroma vector stores over a knowledge base.

- Loads .md, .py and .pdf documents from given directories
- Splits them into chunks and embeds using sentence-transformers via LangChain
- Persists the ChromaDB index for later retrieval
- Provides progress logs via a queue back to the GUI
"""

# src/core/rag_builder.py

import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class RAGBuilder:
    def __init__(self):
        self.index = None
        self.embedding_model="all-MiniLM-L6-v2"

    def _log(self, queue, message):
        """Helper to put a log message in the queue."""
        queue.put(("log", {"sender": "RAGBuilder", "message": message}))

    def build_index(self, knowledge_base_paths, queue, persist_directory, embedding_model="all-MiniLM-L12-v2"):
        """
        Builds the RAG index from the specified knowledge base paths.
        Accepts a list of paths to index.
        Uses a queue to send progress updates back to the main thread.
        """
        self.embedding_model=embedding_model
        try:
            all_documents = []
            for knowledge_base_path in knowledge_base_paths:
                self._log(queue, f"Starting to build index from: {knowledge_base_path}")

                # 1. Load Documents
                self._log(queue, "Loading documents...")
                loader = DirectoryLoader(knowledge_base_path, glob="**/*.md", loader_cls=TextLoader, show_progress=False)
                documents = loader.load()
                loader1 = DirectoryLoader(knowledge_base_path, glob="**/*.py", loader_cls=TextLoader, show_progress=False)
                documents.extend(loader1.load())

                pdf_loader = DirectoryLoader(knowledge_base_path, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=False)
                pdf_documents = pdf_loader.load()

                documents.extend(pdf_documents)

                if not documents:
                    self._log(queue, f"No .md or .pdf documents found in {knowledge_base_path}")
                    continue

                self._log(queue, f"Loaded {len(documents)} documents from {knowledge_base_path}.")
                all_documents.extend(documents)

            if not all_documents:
                raise ValueError("No .md or .pdf documents found in the specified directories.")

            self._log(queue, f"Total documents loaded: {len(all_documents)}")
            # 2. Split Documents
            self._log(queue, "Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=500)
            chunks = text_splitter.split_documents(all_documents)
            self._log(queue, f"Split into {len(chunks)} chunks.")

            # 3. Generate Embeddings
            self._log(queue, "Initializing sentence-transformer for embeddings...")
            # model_name = "sentence-transformers/all-MiniLM-L6-v2"
            model_name = f"sentence-transformers/{self.embedding_model}"
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': False}
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
                multi_process=True
            )
            self._log(queue, "Embedding model loaded.")

            # 4. Create and Persist Vector Store
            self._log(queue, "Creating and persisting ChromaDB vector store...")
            self.index = Chroma.from_documents(
                chunks,
                embeddings,
                persist_directory=persist_directory
            )
            self._log(queue, f"Index built and persisted to {persist_directory}")

            queue.put(("finish", None))
            return self.index
        except Exception as e:
            queue.put(("error", str(e)))

    def load_index(self, persist_directory="./vector_store"):
        """
        Loads a persisted RAG index from the specified directory.
        """
        if not os.path.exists(persist_directory):
            raise FileNotFoundError(f"Persisted index not found at: {persist_directory}")

        # The embedding function is needed to load the index
        model_name =  f"sentence-transformers/{self.embedding_model}"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
            multi_process=True
        )

        self.index = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return self.index
