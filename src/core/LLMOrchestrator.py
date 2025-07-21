# --- Main Orchestrator Class ---
import google.generativeai as genai
import os
import numpy as np
import pickle
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from .prompt_assembler import PromptAssembler
# from .authentication import get_credentials
import json
from ..tools import sigproc as sigproc_tools
from ..tools import transforms as transforms_tools
from ..tools import utils as utils_tools

class LLMOrchestrator:
    def __init__(self, user_data_description, user_objective, run_id, loaded_data, signal_var_name, fs_var_name, log_queue):
        # 1. Initialize core components
        self.log_queue = log_queue
        self.prompt_assembler = PromptAssembler()
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        # Load the pre-built vector store from disk
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
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

        self.user_data_description = user_data_description
        self.user_objective = user_objective
        self.loaded_data = loaded_data
        self.signal_var_name = signal_var_name
        self.fs_var_name = fs_var_name
        self.metaknowledge = None  # Will be populated in the first step
        self.pipeline_steps = []   # This is our "script" as a list of Action objects
        self.max_iterations = 10   # A safety break to prevent infinite loops

    # --- Main Public Method ---

    def run_analysis_pipeline(self):
        """The main entry point to start the entire autonomous analysis process."""
        final_script = []
        # === PHASE 1: INITIALIZATION & FIRST ACTION ===
        self.tools_list = self._get_available_tools()
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
        self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {initial_action.get('tool_name')} ---"}))

        # Execute the initial data loading action
        initial_result = self._execute_current_pipeline()
        # evaluation = self._evaluate_result(current_result, next_action)
        # Send message to GUI to add this step to the flowchart and display its plot
        self.log_queue.put(("flowchart_add_step", {
            "action_id": initial_action.get('action_id'),
            "tool_name": initial_action.get('tool_name'),
            "output_variable": initial_action.get('output_variable'),
            "image_path": initial_result.get('image_path') # Pass the image path from the result
        }))
        
        # For the prototype, we might stop after proposing the first action
        # The original initial_action logic now becomes the first *proposed* analysis action
        first_analysis_action = self._propose_next_action(last_result=initial_result)
        self.pipeline_steps.append(first_analysis_action)
        self.log_queue.put(("log", {"sender": "System", "message": f"--- PROPOSED STEP: {first_analysis_action.get('tool_name')} ---"}))

        second_result = self._execute_current_pipeline()
        # evaluation = self._evaluate_result(current_result, next_action)
        # Send message to GUI for the first analysis action
        self.log_queue.put(("flowchart_add_step", {
            "action_id": first_analysis_action.get('action_id'),
            "tool_name": first_analysis_action.get('tool_name'),
            "output_variable": first_analysis_action.get('output_variable'),
            "image_path": second_result.get('image_path') # Pass the image path from the result
        }))

        # final_script = self._translate_actions_to_code()
        # self.log_queue.put(("log", {"sender": "Code Translator", "message": f"\n--- Python Script ---\n {final_script} \n--------------------------\n"}))
        
        return 0
        # === FULL IMPLEMENTATION: MAIN LOOP ===
        print("Phase 2: Entering Main Loop...")
        for i in range(self.max_iterations):
            print(f"--- Iteration {i+1} ---")
            
            # 1. Propose the next action based on the last result
            # last_result = self._execute_current_pipeline() # This will execute the *entire* pipeline up to this point
            
            next_action = self._propose_next_action(last_result)
            self.pipeline_steps.append(next_action)

            # 2. Execute and evaluate the *new* state of the pipeline
            current_result = self._execute_current_pipeline()
            evaluation = self._evaluate_result(current_result, next_action)

            # 3. Handle self-correction if the step was not useful
            if not evaluation['is_useful']:
                was_refined = self._attempt_refinement(last_action=next_action)
                if not was_refined:
                    self.pipeline_steps.pop() # Remove the failed action
                continue # Move to the next iteration
            
            # Send message to GUI for subsequent analysis actions
            self.log_queue.put(("flowchart_add_step", {
                "action_id": next_action.get('action_id'),
                "tool_name": next_action.get('tool_name'),
                "output_variable": next_action.get('output_variable'),
                "image_path": second_result.get('image_path') # Pass the image path from the result
            }))

            # 4. Check for termination condition
            if self._is_analysis_complete(current_result):
                print("Analysis complete.")
                break
        
        # === FINAL OUTPUT ===
        print("Phase 3: Generating Final Script...")
        final_script = self._translate_actions_to_code()
        return final_script

    # --- Private Helper Methods ---

    def _create_metaknowledge(self):
        """Uses a static prompt to convert user text into a structured JSON."""
        context_bundle = {
            "raw_signal_data": self.loaded_data[self.signal_var_name],
            "sampling_frequency": self.loaded_data[self.fs_var_name][0] if self.fs_var_name else 1,
            "user_data_description": self.user_data_description,
            "user_analysis_objective": self.user_objective,
            "rag_retriever": self.rag_retriever,
            "rag_retriever_tools": self.rag_retriever_tools,
            "tools_list": self.tools_list
        }
        
        prompt = self.prompt_assembler.build_prompt(
            prompt_type="METAKNOWLEDGE_CONSTRUCTION",
            context_bundle=context_bundle
        )
        
        # For now, we'll just print the prompt to the console.
        # The next step would be to send this to the Gemini API.
        print("--- METAKNOWLEDGE PROMPT ---")
        print(prompt)
        print("--------------------------")
        self.log_queue.put(("log", {"sender": "Prompt Assembler", "message": f"--- METAKNOWLEDGE PROMPT ---\n {prompt} \n--------------------------"}))

        # Placeholder for the response
        try:
            # credentials = get_credentials()
            # genai.configure(credentials=credentials)
            
            response = self.model.generate_content(prompt)
            
            # Clean up the response text
            response_text = response.text.strip().replace('```json', '').replace('```', '')
            self.metaknowledge = json.loads(response_text)
            if self.fs_var_name is None:
                self.fs_var_name = 'fs'
                self.loaded_data[self.fs_var_name] = int(self.metaknowledge['data_summary']['sampling_frequency_hz'])
            # print("-----------------------------")
            self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- METAKNOWLEDGE RESPONSE ---\n {self.metaknowledge} \n--------------------------"}))

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            self.metaknowledge = {"status": "error", "message": str(e)}

    def _propose_next_action(self, last_result):
        """Asks the LLM to propose the next tool to use."""
        # context_bundle = {
        #     "metaknowledge": self.metaknowledge,
        #     "last_result": last_result,
        #     "raw_signal_data": self.loaded_data[self.signal_var_name],
        #     "sampling_frequency": self.loaded_data[self.fs_var_name][0],
        #     "user_data_description": self.user_data_description,
        #     "user_analysis_objective": self.user_objective,
        #     "rag_retriever": self.rag_retriever,
        #     "rag_retriever_tools": self.rag_retriever_tools,
        #     "tools_list": self.tools_list
        # }
        # prompt = self.prompt_assembler.build_prompt(
        #     prompt_type="SELECT_NEXT_TOOL",
        #     context_bundle=context_bundle
        # )
        # self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- PROMPT FOR NEXT ACTION ---\n {prompt} \n--------------------------"}))
        
        # This is a placeholder for the real implementation that would call the LLM
        prompt = "This is a placeholder prompt."
        self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- PROMPT FOR NEXT ACTION ---\n {prompt} \n--------------------------"}))

        # Placeholder for the response
        # try:
        #     response = self.model.generate_content(prompt)
        #     # Clean up the response text
        #     response_text = response.text.strip().replace('```json', '').replace('```', '')
        #     self.metaknowledge = json.loads(response_text)
        #     self.log_queue.put(("log", {"sender": "LLM Orchestrator", "message": f"--- NEXT TOOL RESPONSE ---\n {self.metaknowledge} \n--------------------------"}))

        # except Exception as e:
        #     print(f"Error calling Gemini API: {e}")
        #     self.metaknowledge = {"status": "error", "message": str(e)}

        
        # return {
        #     "action_id": len(self.pipeline_steps), # Assign a new action ID
        #     "tool_name": "create_fft_spectrum", # Placeholder for actual LLM proposal
        #     "params": {
        #         "input_signal": "loaded_signal", # Use the output of the load_data action
        #         # "sampling_frequency": self.fs_var_name,
        #         "image_path": os.path.join(self.state_dir, f"step{len(self.pipeline_steps)}_fft_spectrum.png")
        #     },
        #     "output_variable": "fft_spectrum"
        # }

        # return {
        #     "action_id": len(self.pipeline_steps), # Assign a new action ID
        #     "tool_name": "create_signal_spectrogram", # Placeholder for actual LLM proposal
        #     "params": {
        #         "input_signal": "loaded_signal", # Use the output of the load_data action
        #         # "sampling_frequency": self.fs_var_name,
        #         "image_path": os.path.join(self.state_dir, f"step{len(self.pipeline_steps)}_spectrogram.png"),
        #         "nperseg": 256,
        #         "noverlap": 220
        #     },
        #     "output_variable": "spectrogram"
        # }
    
        return {
            "action_id": len(self.pipeline_steps), # Assign a new action ID
            "tool_name": "create_csc_map", # Placeholder for actual LLM proposal
            "params": {
                "input_signal": "loaded_signal", # Use the output of the load_data action
                # "sampling_frequency": self.fs_var_name,
                "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_csc.png"),
                "min_alpha": 1,
                "max_alpha": 200,
                "nperseg": 512,
                "noverlap": 450
            },
            "output_variable": "csc_map"
        }

        # return {
        #     "action_id": len(self.pipeline_steps), # Assign a new action ID
        #     "tool_name": "bandpass_filter", # Placeholder for actual LLM proposal
        #     "params": {
        #         "input_signal": "loaded_signal", # Use the output of the load_data action
        #         # "sampling_frequency": self.fs_var_name,
        #         "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_bandpass_filter.png"),
        #         "lowcut_freq": 1500,
        #         "highcut_freq": 3500,
        #         "order": 10
        #     },
        #     "output_variable": "bandpass_filter"
        # }
    
        # return {
        #     "action_id": len(self.pipeline_steps), # Assign a new action ID
        #     "tool_name": "lowpass_filter", # Placeholder for actual LLM proposal
        #     "params": {
        #         "input_signal": "loaded_signal", # Use the output of the load_data action
        #         # "sampling_frequency": self.fs_var_name,
        #         "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_lowpass_filter.png"),
        #         "cutoff_freq": 1500,
        #         "order": 4
        #     },
        #     "output_variable": "lowpass_filter"
        # }

        # return {
        #     "action_id": len(self.pipeline_steps), # Assign a new action ID
        #     "tool_name": "highpass_filter", # Placeholder for actual LLM proposal
        #     "params": {
        #         "input_signal": "loaded_signal", # Use the output of the load_data action
        #         # "sampling_frequency": self.fs_var_name,
        #         "image_path": os.path.join(self.state_dir, f"step_{len(self.pipeline_steps)}_highpass_filter.png"),
        #         "cutoff_freq": 1500,
        #         "order": 4
        #     },
        #     "output_variable": "highpass_filter"
        # }

    def _execute_current_pipeline(self):
        """Translates the action list to code and executes it in a separate process."""
        import tempfile
        import subprocess
        import os
        import json
        
        # Generate the script code
        script_code = self._translate_actions_to_code()
        self.log_queue.put(("log", {"sender": "System", "message": f"--- GENERATED SCRIPT ---\n {script_code} \n--------------------------"}))
        # Create a temporary Python script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.state_dir) as tmpfile:
            tmpfile.write(script_code)
            temp_script_path = tmpfile.name
            
        try:
            python_executable = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'venv', 'Scripts', 'python.exe')
            command = [python_executable, temp_script_path]
            current_working_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Set CWD to project root

            # self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"Executing command: {command}"}))
            # self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"CWD for subprocess: {current_working_directory}"}))

            execution_result = {
                'data': None,
                'image_path': None
                # 'raw_output': None,
                # 'raw_error': None,
                # 'return_code': None
            }

            try:
                # self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"Attempting to run subprocess with command: {command}"}))
                result0 = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=current_working_directory,  # Run from project root
                    timeout=150 # Add a timeout of 60 seconds to prevent indefinite hanging
                )
                
                # self.run_id
                result_path = os.path.join(self.state_dir, f"current_result_{self.run_id}.pkl")
                with open(result_path, 'rb') as f:
                    result = pickle.load(f)
                
                # Parse execution results
                # output = result.stdout
                # error = result.stderr # Capture stderr even on success for completeness

                # self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"Subprocess STDOUT length: {len(output)}"}))
                # self.log_queue.put(("log", {"sender": "LLM Orchestrator (Debug)", "message": f"Subprocess STDERR length: {len(error)}"}))
                # if error:
                #     self.log_queue.put(("log", {"sender": "LLM Orchestrator (Error)", "message": f"Subprocess STDERR:\n{error}"}))

                # Attempt to extract image_path from the script's output if available
                image_path = None
                try:
                    # Assuming the script might print the image path or a JSON result
                    # This is a very basic parsing; a robust solution would involve
                    # the script writing a structured JSON output to a known file.
                    # import re
                    # match = re.search(r"'image_path': '(.*?)'", result)
                    # if match:
                    #     image_path = match.group(1)
                    image_path = result.get('image_path')
                    # self.log_queue.put(("log", {"sender": "System", "message": f"Image path for current step: {image_path}"}))
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
            "quantitative_results": result,
            "rag_context_for_evaluation": self.rag_retriever.get_relevant_documents("interpret " + action_taken['tool_name']),
            "rag_context_for_evaluation_tools": self.rag_retriever_tools.get_relevant_documents("interpret " + action_taken['tool_name'])
        }

        # 2. It calls the assembler to build the prompt

        # 
        # interpret last action and results
        # powiedzieć o image_path i supporting_image_paths

        # final_prompt = self.prompt_assembler.build_prompt(
        #     prompt_type="EVALUATE_LOCAL_CRITERION",
        #     context_bundle=context_bundle
        # )

        # 3. It sends the final prompt to the API
        # response_json = self.api_client.call_multimodal(final_prompt, image=result.get('image_data'))
        # return parse_json(response_json)
        print("Evaluate result not yet implemented")
        return None

    def _attempt_refinement(self, last_action, result):
        """Asks the LLM if the failed action can be fixed by tuning parameters."""
        # This method would prompt the LLM to suggest new parameters for the failed action.
        # If it suggests new parameters, it modifies the last item in self.pipeline_steps.
        # Returns True if refinement was successful, False otherwise.
        # context_bundle = {
        #     "metaknowledge": self.metaknowledge,
        #     "last_action": last_action,
        #     "quantitative_results": self.parameterization_module.calculate_metrics(result),
        #     "rag_context_for_evaluation": self.rag_retriever.get_relevant_documents("interpret " + last_action['tool_name']),
        #     "rag_context_for_evaluation_tools": self.rag_retriever_tools.get_relevant_documents("interpret " + action_taken['tool_name'])
        # }
        # final_prompt = self.prompt_assembler.build_prompt(
        #     prompt_type="ATTEMPT_REFINEMENT",
        #     context_bundle=context_bundle
        # )
        # response_json = self.api_client.call_multimodal(final_prompt, image=result.get('image_data'))
        # return parse_json(response_json)
        print("Attempt refinement not yet implemented")
        return False

    def _is_analysis_complete(self, last_result, last_action):
        """Asks the LLM if the main objective has been met."""
        # This method uses a prompt to ask for a final yes/no decision.
        # Returns True or False.
        # context_bundle = {
        #     "metaknowledge": self.metaknowledge,
        #     "pipeline_steps": self.pipeline_steps,
        #     "last_result": last_result,
        #     "quantitative_results": self.parameterization_module.calculate_metrics(last_result),
        #     "rag_context_for_evaluation": self.rag_retriever.get_relevant_documents("interpret " + last_action['tool_name']),
        #     "rag_context_for_evaluation_tools": self.rag_retriever_tools.get_relevant_documents("interpret " + action_taken['tool_name'])
        # }
        # final_prompt = self.prompt_assembler.build_prompt(
        #     prompt_type="EVALUATE_GLOBAL_CRITERION",
        #     context_bundle=context_bundle
        # )
        # response_json = self.api_client.call_multimodal(final_prompt, image=result.get('image_data'))
        # return parse_json(response_json)
        print("Is analysis complete not yet implemented")
        return False

    def _get_available_tools(self, tools_dir='src/tools'):
        """
        Scans the tools directory to find all available Python tool scripts.
        """
        available_tools = []
        for root, _, files in os.walk(tools_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    tool_name = os.path.splitext(file)[0]
                    available_tools.append(tool_name)
        # print(f"Available tools: {available_tools}")
        self.log_queue.put(("log", {"sender": "System", "message": f"--- TOOLS---\n {available_tools} \n"}))

        return available_tools

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

        # Add initial data loading for the generated script
        # This assumes self.loaded_data contains the actual signal and fs
        # and self.signal_var_name and self.fs_var_name are the keys for them.
        actual_signal_data = self.loaded_data.get(self.signal_var_name)
        actual_sampling_rate = self.loaded_data.get(self.fs_var_name)

        # Save the signal data to a temporary file
        signal_data_temp_path = os.path.join(self.state_dir, f"signal_data_{self.run_id}.pkl")
        sampling_rate_temp_path = os.path.join(self.state_dir, f"sampling_rate_{self.run_id}.pkl")
        input_image_temp_path = os.path.join(self.state_dir, f"step_0_input_image_{self.run_id}.png")
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
                code_lines.append(f"{output_var}_with_params['image_path'] = {output_var}.get('image_path')")
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

            code_line = f"{output_var}_with_params = calculate_quantitative_metrics({output_var})"
            code_lines.append(code_line)
            # code_lines.append(f'return {output_var}.get("image_path")') # Add a blank line for readability
            code_lines.append("") # Add a blank line
        code_lines.append("with open(result_path, 'wb') as f:")
        code_lines.append(f"    pickle.dump({output_var}_with_params, f)")


        # 5. Join all lines into a single script string
        return "\n".join(code_lines)
