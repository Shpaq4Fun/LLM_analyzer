#!/usr/bin/env python3
"""
Baseline Performance Measurement Script for AIDA

This script measures the current performance of the AIDA system without persistent context.
It loads test data, runs the analysis pipeline, and records metrics like:
- Execution time
- Token usage
- Memory usage
- Success rate
"""

import time
import psutil
import os
import sys
import numpy as np
import scipy.io
from queue import Queue
from threading import Thread

# Add src to path
sys.path.append('src')

from src.core.LLMOrchestrator import LLMOrchestrator
from src.core.authentication import get_credentials

class MockLogQueue:
    """Mock log queue to capture messages instead of sending to GUI"""

    def __init__(self):
        self.messages = []
        self.queue = Queue()

    def put(self, message):
        self.messages.append(message)
        print(f"LOG: {message}")

    def get_messages(self):
        return self.messages

def load_mat_file(filepath):
    """Load MATLAB file and extract signal data"""
    try:
        mat_data = scipy.io.loadmat(filepath)
        print(f"Loaded .mat file with keys: {list(mat_data.keys())}")

        # Find the main signal data (usually the largest array)
        signal_data = None
        fs = None

        for key, value in mat_data.items():
            if not key.startswith('__') and hasattr(value, 'shape'):
                if len(value.shape) == 1 or (len(value.shape) == 2 and min(value.shape) == 1):
                    if signal_data is None or value.size > signal_data.size:
                        signal_data = value.flatten()
                        print(f"Selected signal: {key}, shape: {value.shape}")

        if signal_data is None:
            raise ValueError("No suitable signal data found in .mat file")

        # Assume sampling rate is 1000 Hz if not found
        fs = 1000
        print(f"Using sampling rate: {fs} Hz")

        return signal_data, fs

    except Exception as e:
        print(f"Error loading .mat file: {e}")
        # Fallback to synthetic data
        print("Using synthetic data instead")
        fs = 1000
        t = np.arange(0, 10, 1/fs)
        signal_data = np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*120*t) + 0.1*np.random.randn(len(t))
        return signal_data, fs

def measure_baseline_performance():
    """Main function to measure baseline performance"""

    print("=== AIDA Baseline Performance Measurement ===")

    # Setup authentication
    if not get_credentials():
        print("Authentication failed!")
        return

    # Load test data
    data_path = "data/kruszarka_real4_r4.mat"
    try:
        signal_data, fs = load_mat_file(data_path)
    except:
        print("Using synthetic data")
        fs = 1000
        t = np.arange(0, 10, 1/fs)
        signal_data = np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*120*t) + 0.1*np.random.randn(len(t))

    # Prepare loaded data dict
    loaded_data = {
        'signal': signal_data,
        'fs': fs
    }

    # Setup mock components
    log_queue = MockLogQueue()

    user_description = "Vibration signal from industrial equipment for fault detection"
    user_objective = "Detect bearing faults in the vibration signal"

    # Create orchestrator
    orchestrator = LLMOrchestrator(
        user_data_description=user_description,
        user_objective=user_objective,
        run_id="baseline_test",
        loaded_data=loaded_data,
        signal_var_name='signal',
        fs_var_name='fs',
        log_queue=log_queue
    )

    # Measure initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    print(f"Initial memory usage: {initial_memory:.2f} MB")
    print("Starting analysis pipeline...")

    # Run analysis with timing
    start_time = time.time()

    try:
        orchestrator.run_analysis_pipeline()
        success = True
    except Exception as e:
        print(f"Analysis failed: {e}")
        success = False

    end_time = time.time()

    # Measure final memory
    final_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Calculate metrics
    execution_time = end_time - start_time
    memory_increase = final_memory - initial_memory

    print("\n=== Performance Results ===")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"Initial Memory: {initial_memory:.2f} MB")
    print(f"Final Memory: {final_memory:.2f} MB")
    print(f"Memory Increase: {memory_increase:.2f} MB")
    print(f"Success: {success}")
    print(f"Pipeline Steps: {len(orchestrator.pipeline_steps)}")
    print(f"Result History Length: {len(orchestrator.result_history)}")

    # Save results
    results = {
        'execution_time': execution_time,
        'initial_memory': initial_memory,
        'final_memory': final_memory,
        'memory_increase': memory_increase,
        'success': success,
        'pipeline_steps': len(orchestrator.pipeline_steps),
        'results_count': len(orchestrator.result_history),
        'messages': log_queue.get_messages()
    }

    with open('baseline_results.json', 'w') as f:
        import json
        json.dump(results, f, indent=2, default=str)

    print("Results saved to baseline_results.json")

if __name__ == "__main__":
    measure_baseline_performance()