"""
LLMOrchestrator: Coordinates the end-to-end autonomous analysis pipeline.

Responsibilities:
- Builds prompts and communicates with the LLM
- Manages a sequence of tool-based actions (pipeline)
- Executes pipeline steps as a generated script in a subprocess
- Evaluates results and iteratively proposes next actions
- Interfaces with a GUI via a log_queue for messages and images
"""

import google.generativeai as genai
from difflib import SequenceMatcher
import os
import pickle
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from .prompt_assembler import PromptAssembler
import json

class LLMOrchestrator:
    def __init__(self, user_data_description, user_objective, run_id, loaded_data, signal_var_name, fs_var_name, log_queue):
        # 1. Initialize core components
        self.log_queue = log_queue
        self.prompt_assembler = PromptAssembler()
        self.model_name = "gemini-2.5-pro" # Specific model version
        self.model = genai.GenerativeModel(self.model_name)

        # Load the pre-built vector store from disk
        # all-MiniLM-L6-v2
        # all-mpnet-base-v2
        self.embedding_model = "all-MiniLM-L12-v2"
        embedding_model = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vector_store = Chroma(
            persist_directory="./vector_store",
            embedding_function=embedding_model
        )
        self.vector_store_tools = Chroma(
            persist_directory="./vector_store_tools",
            embedding_function=embedding_model
        )
        # Create a retriever interface for easy searching
        self.rag_retriever = self.vector_store.as_retriever(search_kwargs={"k": 5}) # 'k' is number of results to return
        self.rag_retriever_tools = self.vector_store_tools.as_retriever(search_kwargs={"k": 5}) # 'k' is number of results to return
        # 2. Initialize the state for this specific run
        self.run_id = run_id
        self.state_dir = f"./run_state/{self.run_id}"
        os.makedirs(self.state_dir, exist_ok=True) # Create a directory for this run's state files

        # self._create_caches()
        self.user_data_description = user_data_description
        self.user_objective = user_objective
        self.loaded_data = loaded_data
        self.signal_var_name = signal_var_name
        self.fs_var_name = fs_var_name
        self.metaknowledge = None  # Will be populated in the first step
        self.pipeline_steps = []   # This is our "script" as a list of Action objects
        self.result_history = []
        self.eval_history = []
        self.max_iterations = 20   # A safety break to prevent infinite loops

    # --- Main Public Method ---
    def run_analysis_pipeline(self):
        """The main entry point to start the entire autonomous analysis process."""
        final_script = []
        # === PHASE 1: INITIALIZATION & FIRST ACTION ===
        print("Phase 1: Initialization & First Action...")
        self._create_metaknowledge()
        
        # The first action is always loading the data
        initial_action = {
            "action_id": 0, # Action ID 0 for data loading
            "tool_name": "load_data",
            "params": {
                "signal_data": self.signal_var_name,
                "sampling_rate": self.fs_var_name,
                "output_image_path": os.path.join(self.state_dir, "step0_loaded_data.png")
            },
            "output_variable": "loaded_signal"
        }
        self.pipeline_steps.append(initial_action)
        # self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {initial_action.get('tool_name')} ---"}))
        
        # Execute the initial data loading action
        initial_result = self._execute_current_pipeline()
        # Send message to GUI to add this step to the flowchart and display its plot
        self.log_queue.put(("flowchart_add_step", {
            "action_id": initial_action.get('action_id'),
            "tool_name": initial_action.get('tool_name'),
            "output_variable": initial_action.get('output_variable'),
            "image_path": initial_result.get('image_path') # Pass the image path from the result
        }))
        
        self.result_history.append(initial_result)

        # Evaluate the initial data loading action
        evaluation = self._evaluate_result(initial_result, initial_action)
        # print(evaluation)
        # self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {json.dumps(evaluation, indent=4)} ---"}))
        
        # print(evaluation)

        # The original initial_action logic now becomes the first *proposed* analysis action
        first_analysis_action = self._fetch_next_action(evaluation)
        self.pipeline_steps.append(first_analysis_action)
        # self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {first_analysis_action.get('tool_name')} ---"}))
        
        second_result = self._execute_current_pipeline()
        # Send message to GUI for the first analysis action
        self.log_queue.put(("flowchart_add_step", {
            "action_id": first_analysis_action.get('action_id'),
            "tool_name": first_analysis_action.get('tool_name'),
            "output_variable": first_analysis_action.get('output_variable'),
            "image_path": second_result.get('image_path') # Pass the image path from the result
        }))

        
        self.result_history.append(second_result)

        evaluation = self._evaluate_result(second_result, first_analysis_action)
        

        # final_script = self._translate_actions_to_code()
        # self.log_queue.put(("log", {"sender": "Code Translator", "message": f"\n--- Python Script ---\n {final_script} \n--------------------------\n"}))
        
        # === FULL IMPLEMENTATION: MAIN LOOP ===
        print("Phase 2: Entering Main Loop...")
        for i in range(self.max_iterations):
            print(f"--- Iteration {i+1} ---")
            
            # 1. Propose the next action based on the last result
            # last_result = self._execute_current_pipeline() # This will execute the *entire* pipeline up to this point
            
            current_action = self._fetch_next_action(evaluation)
            self.pipeline_steps.append(current_action)
            # self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {current_action.get('tool_name')} ---"}))
            current_result = self._execute_current_pipeline()
            # Send message to GUI for subsequent analysis actions
            self.log_queue.put(("flowchart_add_step", {
                "action_id": current_action.get('action_id'),
                "tool_name": current_action.get('tool_name'),
                "output_variable": current_action.get('output_variable'),
                "image_path": current_result.get('image_path') # Pass the image path from the result
            }))

            # 2. Execute and evaluate the *new* state of the pipeline
            
            self.result_history.append(current_result)

            evaluation = self._evaluate_result(current_result, current_action)
            # print(evaluation)
            

            # return 0
            # 4. Check for termination condition
            if json.loads(evaluation).get("is_final"):
                self.log_queue.put(("log", {"sender": "System", "message": f"--- ANALYSIS COMPLETE ---"}))
                www = "\n\n".join(self.eval_history)
                self.log_queue.put(("log", {"sender": "System", "message": f"--- REASONING HISTORY ---\n\n {www}\n ---\n"}))
                # self.log_queue.put(("log", {"sender": "System", "message": f"--- THANK YOU FOR FLYING BIEDRONKA AIRLINES ---\n"}))
                break
        
        # # === FINAL OUTPUT ===
        # print("Phase 3: Generating Final Script...")
        # final_script = self._translate_actions_to_code()
        # return final_script
    
    # --- Private Helper Methods ---
    def _generate_content_with_fallback(self, prompt):
        """
        Attempts to generate content using the current model, falling back to other models if needed.
        Returns the response object and logs the active model.
        """
        try:
            try:
                response = self.model.generate_content(prompt)
            except:
                try:
                    self.model_name = "gemini-2.5-flash"
                    self.model = genai.GenerativeModel("gemini-2.5-flash")
                    response = self.model.generate_content(prompt)
                except:
                    try:
                        self.model_name = "gemini-2.0-pro"
                        self.model = genai.GenerativeModel("gemini-2.0-pro")
                        response = self.model.generate_content(prompt)
                    except:
                        try:
                            self.model_name = "gemini-2.0-flash"
                            self.model = genai.GenerativeModel("gemini-2.0-flash")
                            response = self.model.generate_content(prompt)
                        except:
                            try:
                                self.model_name = "gemini-1.5-pro"
                                self.model = genai.GenerativeModel("gemini-1.5-pro")
                                response = self.model.generate_content(prompt)
                            except:
                                self.model_name = "gemini-1.5-flash"
                                self.model = genai.GenerativeModel("gemini-1.5-flash")
                                response = self.model.generate_content(prompt)
            self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- ACTIVE MODEL: {self.model_name} ---"}))
            return response
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {e}")

    def _create_metaknowledge(self):
        """Uses a static prompt to convert user text into a structured JSON."""
        context_bundle = {
            "raw_signal_data": self.loaded_data[self.signal_var_name],
            "sampling_frequency": self.loaded_data[self.fs_var_name][0] if self.fs_var_name else 1,
            "user_data_description": self.user_data_description,
            "user_analysis_objective": self.user_objective,
            "rag_retriever": self.rag_retriever,
            "rag_retriever_tools": self.rag_retriever_tools,
            "tools_list": self._get_available_tools()
        }
        
        prompt = self.prompt_assembler.build_prompt(
            prompt_type="METAKNOWLEDGE_CONSTRUCTION",
            context_bundle=context_bundle
        )
        
        # Generation of the response by the LLM trying the best models first.
        try:
            response = self._generate_content_with_fallback(prompt)
            # Clean up the response text
            response_text = response.text.strip().replace('```json', '').replace('```', '')
            self.metaknowledge = json.loads(response_text)
            sss = json.dumps(self.metaknowledge, indent=4)
            if self.fs_var_name is None:
                self.fs_var_name = 'fs'
                self.loaded_data[self.fs_var_name] = int(self.metaknowledge['data_summary']['sampling_frequency_hz'])
            # print("-----------------------------")
            self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- METAKNOWLEDGE RESPONSE ---\n {sss} \n--------------------------"}))

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            self.metaknowledge = {"status": "error", "message": str(e)}

    def _fetch_next_action(self, evaluation):
        """Returns JSON object of the next tool to use."""
        input_variable = json.loads(evaluation).get('input_variable')
        params = json.loads(evaluation).get("params")
        if len(params)>0:
            param_keys = params.keys()
        else:
            param_keys = []

        accept_ratio = 0.7
        match json.loads(evaluation).get("tool_name"):
            case "create_fft_spectrum":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "create_fft_spectrum", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_fft_spectrum.png")
                    },
                    "output_variable": f"fft_spectrum_{len(self.pipeline_steps)}"
                }
                return action
            case "create_envelope_spectrum":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "create_envelope_spectrum", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_env_spectrum.png")
                    },
                    "output_variable": f"envelope_spectrum_{len(self.pipeline_steps)}"
                }
                return action
            case "create_signal_spectrogram":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "create_signal_spectrogram", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_spectrogram.png"),
                        "window": 256,
                        "noverlap": 220
                    },
                    "output_variable": f"spectrogram_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "create_csc_map":
                # params = json.loads(evaluation).get("params")
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "create_csc_map", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_csc.png"),
                        "min_alpha": 1,
                        "max_alpha": 150,
                        "window": 512,
                        "noverlap": 450
                    },
                    "output_variable": f"csc_map_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "bandpass_filter":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "bandpass_filter", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        # "sampling_frequency": self.fs_var_name,
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_bandpass_filter.png"),
                        "lowcut_freq": 1500,
                        "highcut_freq": 3500,
                        "order": 10
                    },
                    "output_variable": f"bp_filter_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "lowpass_filter":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "lowpass_filter", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        # "sampling_frequency": self.fs_var_name,
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_lowpass_filter.png"),
                        "cutoff_freq": 1500,
                        "order": 4
                    },
                    "output_variable": f"lp_filter_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "highpass_filter":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "highpass_filter", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        # "sampling_frequency": self.fs_var_name,
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_highpass_filter.png"),
                        "cutoff_freq": 1500,
                        "order": 4
                    },
                    "output_variable": f"hp_filter_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "decompose_matrix_nmf":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "decompose_matrix_nmf", # Placeholder for actual LLM proposal
                    "params": {
                        "input_signal": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_decompose_matrix_nmf.png"),
                        "n_components": 3,
                        "max_iter": 150,
                    },
                    "output_variable": f"nmf_results_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action
            case "select_component":
                action = {
                    "action_id": len(self.pipeline_steps), # Assign a new action ID
                    "tool_name": "select_component", # Placeholder for actual LLM proposal
                    "params": {
                        "data": input_variable, # Use the output of the load_data action
                        "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_selected_component.png"),
                        "component_index": 0
                    },
                    "output_variable": f"selected_component_{len(self.pipeline_steps)}"
                }
                for key in param_keys:
                    for key_orig in action['params'].keys():
                        ratio = SequenceMatcher(None, key, key_orig).ratio()
                        print(f"Comparing {key} with {key_orig}: ratio {ratio}")
                        if ratio > accept_ratio:
                            print(f"Replacing {key_orig} with the value from {key} ")
                            action['params'][key_orig] = params[key]
                return action

    def _execute_current_pipeline(self):
        """Translates the action list to code and executes it in a separate process."""
        import tempfile
        import subprocess
        
        # Generate the script code
        script_code = self._translate_actions_to_code()
        self.log_queue.put(("log", {"sender": "Prompt Translator", "message": f"--- GENERATED SCRIPT ---\n{script_code} \n--------------------------"}))
        # Create a temporary Python script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.state_dir) as tmpfile:
            tmpfile.write(script_code)
            temp_script_path = tmpfile.name
            
        try:
            python_executable = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'venv', 'Scripts', 'python.exe')
            command = [python_executable, temp_script_path]
            current_working_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Set CWD to project root

            # Initialize execution_result
            execution_result = {
                'data': None,
                'image_path': None
                # 'raw_output': None,
                # 'raw_error': None,
                # 'return_code': None
            }

            try:
                result0 = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=current_working_directory,  # Run from project root
                    timeout=1500 # Add a timeout of 60 seconds to prevent indefinite hanging
                )
                
                result_path = os.path.join(self.state_dir, f"current_result_{self.run_id}.pkl")
                with open(result_path, 'rb') as f:
                    result = pickle.load(f)
                
            
                # Attempt to extract image_path from the script's output if available
                image_path = None
                try:
                    image_path = result.get('image_path')
                except Exception as e:
                    self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"Warning: Could not extract image path from script output: {e}"}))
                
                # Populate execution_result
                execution_result = {
                    'data': result,
                    'image_path': image_path
                    # 'raw_output': result
                    # 'return_code': result.returncode
                }
                # Send the image path to the GUI
                if image_path:
                    self.log_queue.put(("image_display", {"image_path": image_path}))
                else:
                    self.log_queue.put(("log", {"sender": "System", "message": "No image path provided by the tool"}))
                
            except subprocess.TimeoutExpired as e:
                self.log_queue.put(("log", {"sender": "LLM Orchestrator (Error)", "message": f"Script execution timed out after {e.timeout} seconds.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"}))
                raise # Re-raise the exception to propagate the failure
            except subprocess.CalledProcessError as e:
                self.log_queue.put(("log", {"sender": "LLM Orchestrator (Error)", "message": f"Script execution failed with exit code {e.returncode}:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"}))
                # Re-raise or handle as appropriate for the orchestrator's flow
                raise # Re-raise the exception to propagate the failure
        except Exception as e:
            self.log_queue.put(("log", {"sender": "LLM Orchestrator (Error)", "message": f"An unexpected error occurred during script execution: {e}"}))
            raise # Re-raise the exception
        finally:
            pass
            # Clean up temporary file
            # os.unlink(temp_script_path)
        return execution_result # This return statement should be at the same level as the try block

    def _evaluate_result(self, result, action_taken):
        """Asks the LLM to evaluate the result of the last action, possibly multimodal."""
        # 1. Orchestrator gathers the context
        context_bundle = {
            "metaknowledge": self.metaknowledge,
            "last_action": action_taken,
            "last_result": result,
            "sequence_steps": self.pipeline_steps,
            "rag_retriever": self.rag_retriever,
            "rag_retriever_tools": self.rag_retriever_tools,
            "tools_list": self._get_available_tools(),
            "user_data_description": self.user_data_description,
            "user_analysis_objective": self.user_objective,
            "result_history": self.result_history
        }
        
        # 2. It calls the assembler to build the prompt

        # 
        # interpret last action and results
        # powiedzieć o image_path i supporting_image_paths

        prompt = self.prompt_assembler.build_prompt(
            prompt_type="EVALUATE_LOCAL_CRITERION",
            context_bundle=context_bundle
        )
        try:
            response = self._generate_content_with_fallback(prompt)

            # response = self.genai_client.models.generate_content(prompt)
            # aaa = json.dumps(response_text, indent=6)
            # Clean up the response text
            evaluation = response.text.strip().replace('```json', '').replace('```', '')

            # text_description, self.proposed_action = self.extract_text_and_json(response_text)
            text_description = json.loads(evaluation).get('evaluation_summary')
            proposed_action = json.loads(evaluation).get("tool_name")
            input_variable = json.loads(evaluation).get('input_variable')
            params = json.loads(evaluation).get("params")
            is_final = json.loads(evaluation).get("is_final")
            justification = json.loads(evaluation).get("justification")
            print(json.dumps(text_description, indent=4))
            print(proposed_action)
            # print(input_variable)
            # print(params)
            # print(params.keys())
            self.eval_history.append(text_description)

            self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- RESULT EVALUATION RESPONSE ---\n Evaluation summary: {text_description} \n Proposed action: {json.dumps(proposed_action, indent=4)} \n Input variable: {input_variable} \n Justification: {justification} \n Custom parameters: {params} \n Action final: {is_final}\n--------------------------"}))

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            evaluation = {"status": "error", "message": str(e)}
        return evaluation

    def _get_available_tools(self, tools_reference_path='src/docs/TOOLS_REFERENCE.md'):
        """
        Loads the content of the TOOLS_REFERENCE.md file for better API description.
        """
        try:
            with open(tools_reference_path, 'r', encoding='utf-8') as f:
                tools_reference_content = f.read()

            self.log_queue.put(("log", {"sender": "System", "message": f"--- TOOLS REFERENCE LOADED ---\n {tools_reference_path} \n"}))
            return tools_reference_content

        except FileNotFoundError:
            self.log_queue.put(("log", {"sender": "System", "message": f"--- ERROR: TOOLS REFERENCE FILE NOT FOUND ---\n {tools_reference_path} \n"}))
            return "Tools reference file not found."
        except Exception as e:
            self.log_queue.put(("log", {"sender": "System", "message": f"--- ERROR LOADING TOOLS REFERENCE ---\n {str(e)} \n"}))
            return f"Error loading tools reference: {str(e)}"

    def _translate_actions_to_code(self):
        """
        Deterministically translates the internal list of Action objects into a
        single, executable Python script string.
        """
        # 1. Start with necessary imports
        code_lines = [
            "import numpy as np",
            "import pickle", # For the long-term state management
            "import sys",
            "import os",
            "", # Add a blank line for readability
            "# Add the project root to sys.path to enable absolute imports for the 'src' package",
            "sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))",
            "from src.core.quantitative_parameterization_module import calculate_quantitative_metrics",
            "" # Add a blank line for readability
        ]

        # Map tool names to their respective submodules
        tool_submodule_map = {
            "bandpass_filter": "sigproc",
            "highpass_filter": "sigproc",
            "lowpass_filter": "sigproc",
            "create_csc_map": "transforms",
            "create_envelope_spectrum": "transforms",
            "create_fft_spectrum": "transforms",
            "create_signal_spectrogram": "transforms",
            "load_data": "utils", # Add the new tool
            "select_component": "decomposition",
            "decompose_matrix_nmf": "decomposition"
        }

        # Collect unique submodules needed for the current pipeline
        needed_submodules = set()
        for action in self.pipeline_steps:
            tool_name = action.get('tool_name')
            if tool_name in tool_submodule_map:
                needed_submodules.add(tool_submodule_map[tool_name])
        
        # Add imports for the needed tools to the script
        # We need to import each tool function directly from its module
        for action in self.pipeline_steps:
            tool_name = action.get('tool_name')
            submodule = tool_submodule_map.get(tool_name)
            if submodule:
                # Import the specific function from its module
                code_lines.append(f"from src.tools.{submodule}.{tool_name} import {tool_name}")
        code_lines.append("") # Add a blank line for readability

        # and self.signal_var_name and self.fs_var_name are the keys for them.
        actual_signal_data = self.loaded_data.get(self.signal_var_name)
        actual_sampling_rate = self.loaded_data.get(self.fs_var_name)

        # Save the signal data to a temporary file
        signal_data_temp_path = os.path.join(self.state_dir, f"signal_data_{self.run_id}.pkl")
        sampling_rate_temp_path = os.path.join(self.state_dir, f"sampling_rate_{self.run_id}.pkl")
        input_image_temp_path = os.path.join(self.state_dir, f"step_0_input_image.png")
        result_temp_path = os.path.join(self.state_dir, f"current_result_{self.run_id}.pkl")
        with open(signal_data_temp_path, 'wb') as f:
            pickle.dump(actual_signal_data, f)
        with open(sampling_rate_temp_path, 'wb') as f:
            pickle.dump(actual_sampling_rate, f)
        # Add code to load the signal data from the temporary file
        code_lines.append(f"signal_data_path = '{signal_data_temp_path}'")
        code_lines.append(f"sampling_rate_path = '{sampling_rate_temp_path}'")
        code_lines.append(f"input_image_path = '{input_image_temp_path}'")
        code_lines.append(f"result_path = '{result_temp_path}'")
        code_lines.append("with open(signal_data_path, 'rb') as f:")
        code_lines.append("    signal_data = pickle.load(f)")
        code_lines.append("with open(sampling_rate_path, 'rb') as f:")
        code_lines.append("    fs = int(pickle.load(f))")
        # Sampling rate can still be embedded directly as it's an int
        # code_lines.append(f"{self.fs_var_name} = {actual_sampling_rate}")
        code_lines.append("") # Add a blank line for readability

        # 2. Loop through each action in the pipeline
        for action in self.pipeline_steps:
            # Add a comment to the script for clarity and debugging
            code_lines.append(f"# --- Action {action.get('action_id', 'N/A')}: Executing {action.get('tool_name', 'N/A')} ---")

            # 3. Special handling for load_data output
            if action.get('tool_name') == 'load_data':
                output_var = action.get('output_variable', 'result')
                # After loading data, extract signal and fs from the returned dict
                code_lines.append(f"{output_var} = load_data(signal_data, fs, input_image_path)")
                code_line = f"{output_var}_with_params = calculate_quantitative_metrics({output_var})"
                code_lines.append(code_line)
                # Preserve image_path in the parameterized result
                code_lines.append(f"{output_var}_with_params['image_path'] = {output_var}['image_path']")
                code_lines.append("")  # Blank line for readability
                continue  # Skip normal parameter handling since we've already processed load_data

            # Format parameters for other tools
            param_strings = []
            if 'params' in action and isinstance(action['params'], dict):
                for key, value in action['params'].items():
                    # This is the crucial logic: we need to know if a value is a
                    # string literal or a reference to a variable from a previous step
                    # or a reference to the initial signal/fs variables.
                    
                    is_variable_reference = False
                    if isinstance(value, str):
                        # Check if it's a reference to the initial signal/fs variables
                        if value == self.signal_var_name or value == self.fs_var_name:
                            is_variable_reference = True
                        else:
                            # Check if it's a reference to an output_variable from a previous step
                            for prev_action in self.pipeline_steps:
                                if 'output_variable' in prev_action and value == prev_action['output_variable']:
                                    is_variable_reference = True
                                    break

                    if isinstance(value, str) and not is_variable_reference:
                        # It's a string literal, so wrap it in quotes
                        formatted_value = f"'{value}'"
                    else:
                        # It's a number, boolean, or a recognized variable reference, so use as-is
                        formatted_value = str(value)
                    
                    # param_strings.append(f"{key}={formatted_value}")
                    param_strings.append(f"{formatted_value}")

            # Join the formatted parameters with commas
            params_str = ", ".join(param_strings)

            # 4. Construct the final line of code for this action
            output_var = action.get('output_variable', 'result')
            tool_name = action.get('tool_name', 'unknown_tool')
            
            # Construct the final line of code for this action
            # Now that functions are imported directly, no submodule prefix is needed
            code_line = f"{output_var} = {tool_name}({params_str})"
            code_lines.append(code_line)

            # # Ensure the image_path is in the dictionary before parameterization
            # image_path_value = action.get('params', {}).get('image_path', 'None')
            # if image_path_value != 'None':
            #     code_lines.append(f"if '{output_var}' in locals() and isinstance({output_var}, dict):")
            #     code_lines.append(f"    {output_var}['image_path'] = '{image_path_value}'")

            code_line = f"{output_var} = calculate_quantitative_metrics({output_var})"
            code_lines.append(code_line)
            # code_lines.append(f'return {output_var}.get("image_path")') # Add a blank line for readability
            code_lines.append("") # Add a blank line
        code_lines.append("with open(result_path, 'wb') as f:")
        code_lines.append(f"    pickle.dump({output_var}, f)")


        # 5. Join all lines into a single script string
        return "\n".join(code_lines)
