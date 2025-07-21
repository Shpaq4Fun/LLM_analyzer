# --- prompt_assembler.py ---
import os


# This class is responsible for constructing the exact, final prompt strings
# that will be sent to the LLM API.

class PromptAssembler:
    def __init__(self):
        # Load all the static prompt templates from files into memory
        self.templates = self._load_prompt_templates()

    # === The Dispatcher Method (Public) ===

    def build_prompt(self, prompt_type: str, context_bundle: dict) -> str:
        """
        The main entry point. It takes the desired prompt type and a bundle
        of all necessary context, then routes to the correct handler.
        """
        if prompt_type == "METAKNOWLEDGE_CONSTRUCTION":
            temp_prompt = self._build_metaknowledge_prompt(context_bundle)
        
        elif prompt_type == "EVALUATE_LOCAL_CRITERION":
            temp_prompt =  self._build_evaluate_local_prompt(context_bundle)
            
        elif prompt_type == "EVALUATE_GLOBAL_CRITERION":
            temp_prompt =  self._build_evaluate_global_prompt(context_bundle)
            
        elif prompt_type == "SELECT_NEXT_TOOL":
            temp_prompt =  self._build_select_tool_prompt(context_bundle)
            
        elif prompt_type == "ATTEMPT_REFINEMENT":
            temp_prompt =  self._build_refinement_prompt(context_bundle)
            
        else:
            temp_prompt = []
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        final_prompt = self.templates['meta_template'].format(
            specific_task_prompt=temp_prompt, # A helper function to get our target schema
        )
        return final_prompt

    # === Handler Methods (Private) ===

    def _build_metaknowledge_prompt(self, context_bundle: dict) -> str:
    
    # Handler for creating the prompt that instructs the LLM to generate the
    # structured Metaknowledge JSON object.

    # Args:
    #     context_bundle (dict): A dictionary containing all necessary inputs:
    #         'raw_signal_data' (np.ndarray): The actual 1D vibration signal.
    #         'sampling_frequency' (int): The signal's sampling rate.
    #         'user_data_description' (str): The user's text about the data.
    #         'user_analysis_objective' (str): The user's text about the goal.
    #         'rag_retriever': The retriever object for the knowledge base.

    # Returns:
    #     str: The fully constructed, final prompt string.
    
    
    # === Step 1: Pre-computation of Ground Truth Stats ===
    # Before prompting the LLM, calculate objective facts directly from the data.
    # This prevents the LLM from having to guess these values.
    
        signal_length_sec = len(context_bundle['raw_signal_data']) / context_bundle['sampling_frequency']
        number_of_samples = len(context_bundle['raw_signal_data'])
        
        # Create a formatted string of these ground truth facts.
        ground_truth_summary = f"""- Signal Length: {signal_length_sec:.2f} seconds
    - Total Samples: {number_of_samples}
    - Sampling Frequency: {context_bundle['sampling_frequency']} Hz"""

        # === Step 2: Retrieval of Relevant Context (RAG) ===
        # Query the knowledge base to find context related to the user's description.
        # This helps the LLM understand domain-specific terms like "inner race fault".
        
        # Combine user texts to create a rich query for the RAG index
        rag_query = context_bundle['user_data_description'] + " " + context_bundle['user_analysis_objective']
        retrieved_docs = context_bundle['rag_retriever'].get_relevant_documents(rag_query)
        tools_list = context_bundle['tools_list']
        # retrieved_docs_tools = context_bundle['rag_retriever_tools'].get_relevant_documents(rag_query)  
        
        # Format the retrieved documents into a single string.
        rag_context_str = "\n\n".join([f"Context Snippet {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        rag_context_str_tools = "\n\n".join(tools_list)
        # === Step 3: Assemble the Final Prompt from a Static Template ===
        # Use a pre-defined template and inject all the gathered information.
        
        final_prompt = self.templates['meta_template'].format(
            specific_task_prompt=self.templates['metaknowledge'].format(
            json_schema=self.get_metaknowledge_json_schema_as_string(), # A helper function to get our target schema
            ground_truth_summary=ground_truth_summary,
            rag_context=rag_context_str,
            rag_context_tools=rag_context_str_tools,
            user_data_description=context_bundle['user_data_description'],
            user_analysis_objective=context_bundle['user_analysis_objective']
        ))

        return final_prompt

    def get_metaknowledge_json_schema_as_string(self):
        # In a real application, this would load a JSON schema from a file.
        # For this prototype, we'll define it as a string.
        return """
    {
        "signal_type": "string (e.g., 'vibration', 'acoustic', 'temperature')",
        "machine_type": "string (e.g., 'rotating machinery', 'reciprocating compressor', 'HVAC unit')",
        "component_under_test": "string (e.g., 'rolling element bearing', 'gearbox', 'piston')",
        "fault_type_hypothesis": "string (e.g., 'inner race fault', 'gear tooth wear', 'unbalance')",
        "signal_characteristics": [
            "string (e.g., 'cyclostationary', 'transient', 'non-stationary', 'periodic')"
        ],
        "analysis_objective_tags": [
            "string (e.g., 'fault detection', 'prognostics', 'condition monitoring', 'root cause analysis')"
        ],
        "analysis_objective": {
            "primary_goal": "string",
            "target_fault_type": "string or null",
            "target_signal_feature": "string",
            "fallback_goal": "string or null"
        },
        "initial_hypotheses": "string"
    }
    """

    def _build_evaluate_local_prompt(self, context: dict) -> str:
        """Handler for the 'Are results useful?' decision."""
        # This is a complex assembly of multiple pieces of context
        return self.templates['evaluate_local'].format(
            metaknowledge=context['metaknowledge'],
            last_action=context['last_action'],
            quantitative_results=context['quantitative_results'],
            rag_context=context['rag_context_for_evaluation']
            # Note: The image data is handled separately in the multimodal API call
        )
        
    def _build_select_tool_prompt(self, context: dict) -> str:
        """Handler for proposing the next action."""
        return self.templates['select_tool'].format(
            metaknowledge=context['metaknowledge'],
            pipeline_history=context['pipeline_history'],
            last_result_summary=context['last_result_summary'],
            rag_context=context['rag_context_for_tools'],
            exclusion_list=context.get('exclusion_list', []) # From our guardrails
        )
        
    # ... and so on for the other handlers (_build_evaluate_global_prompt, etc.) ...

    def _load_prompt_templates(self) -> dict:
        """A utility function to load all .txt prompt templates from a directory."""
        templates = {}
        template_dir = "src/prompt_templates"
        for filename in os.listdir(template_dir):
            if filename.endswith(".txt"):
                template_name = filename.replace('_prompt.txt', '')
                with open(os.path.join(template_dir, filename), 'r') as f:
                    templates[template_name] = f.read()
        return templates
