"""
PromptAssembler builds concrete prompts for different stages of the pipeline.

- Loads text templates from src/prompt_templates
- Assembles prompts for: metaknowledge construction, local/global evaluation,
  tool selection, and attempt refinement
- Some handlers are multimodal: they return a list that includes PIL.Image objects
  to be passed to the LLM client alongside text
"""

# --- prompt_assembler.py ---
import os, fnmatch, json
from PIL import Image

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

        else:
            temp_prompt = []
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        # final_prompt = self.templates['meta_template'].format(
        #     specific_task_prompt=temp_prompt, # A helper function to get our target schema
        # )
        return temp_prompt

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
        ground_truth_summary = f"""
- Signal Length: {signal_length_sec:.2f} seconds
    - Total Samples: {number_of_samples}
    - Sampling Frequency: {context_bundle['sampling_frequency']} Hz"""

        # === Step 2: Retrieval of Relevant Context (RAG) ===
        # Query the knowledge base to find context related to the user's description.
        # This helps the LLM understand domain-specific terms like "inner race fault".

        # Combine user texts to create a rich query for the RAG index
        rag_query = context_bundle['user_data_description'] + " " + context_bundle['user_analysis_objective']
        retrieved_docs = context_bundle['rag_retriever'].invoke(rag_query)
        tools_list = context_bundle['tools_list']
        retrieved_docs_tools = context_bundle['rag_retriever_tools'].invoke(rag_query)

        # Format the retrieved documents into a single string.
        rag_context_str = "\n\n".join([f"Context Snippet {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        rag_context_str_tools = "\n\n".join([f"Context Snippet {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs_tools)])
        # tools_list is now already a string containing the content of TOOLS_REFERENCE.md
        # === Step 3: Assemble the Final Prompt from a Static Template ===
        # Use a pre-defined template and inject all the gathered information.

        final_prompt = self.templates['metaknowledge_prompt_v2'].format(
            ground_truth_summary=ground_truth_summary,
            rag_context=rag_context_str,
            rag_context_tools=rag_context_str_tools,
            tools_list=tools_list,
            user_data_description=context_bundle['user_data_description'],
            user_analysis_objective=context_bundle['user_analysis_objective']
        )
        # print(final_prompt)
        return final_prompt

    def _build_evaluate_local_prompt(self, context_bundle: dict) -> str:
        """Handler for the 'Are results useful?' decision."""
        # This is a complex assembly of multiple pieces of context

        # Combine user texts to create a rich query for the RAG index
        rag_query = context_bundle['user_data_description'] + " " + context_bundle['user_analysis_objective'] + " " + context_bundle['last_action'].get('tool_name') + " next steps"
        retrieved_docs = context_bundle['rag_retriever'].invoke(rag_query)
        tools_list = context_bundle['tools_list']
        retrieved_docs_tools = context_bundle['rag_retriever_tools'].invoke(rag_query)
        result_history = context_bundle['result_history']

        # Format the retrieved documents into a single string.
        rag_context_str = "\n\n".join([f"Context Snippet {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        rag_context_str_tools = "\n\n".join([f"Context Snippet {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs_tools)])
        # tools_list is now already a string containing the content of TOOLS_REFERENCE.md

        #TODO: read context_bundle["last_result"]["image_path"] and then iterate over context_bundle["last_result"]["supporting_image_paths"] to get paths to images for evaluation
        ipath = context_bundle["last_result"]["image_path"]
        supporting_image = Image.open(ipath)
        image_prompts = ['Main image for evaluation: ']
        image_prompts.append(ipath.split('\\')[-1])
        image_prompts.append(supporting_image)

        for result in result_history:
            # if len(context_bundle["last_result"]["data"].get("supporting_image_paths",[]))>0:
            if len(result["data"].get("supporting_image_paths",[]))>0:
                image_prompts.append('Supporting images for evaluation (plots of all results):\n')
                for ipath in result["data"].get("supporting_image_paths",[]):
                    # print(ipath+"\n")
                    supporting_image0 = result["data"]["supporting_image_paths"].get(f"{ipath}")
                    supporting_image = Image.open(supporting_image0)
                    image_prompts.append(ipath.split('/')[-1])
                    image_prompts.append(supporting_image)

        action_documentation_path = ""
        fname = context_bundle["last_action"].get('tool_name') + ".md"
        for root, dirs, files in os.walk('src/tools/',topdown=True):
            # print(files)
            for name in files:
                if fnmatch.fnmatch(name, fname):
                    action_documentation_path = os.path.join(root, name)
                    break


        with open(action_documentation_path, 'r') as f:
            fileString = f.read()
            tool_doc = fileString
        last_result_params = context_bundle['last_result']['data']['new_params'] if 'new_params' in context_bundle['last_result']['data'] else {}
        prompt0 = self.templates['evaluate_local_prompt_v2'].format(
            metaknowledge=context_bundle['metaknowledge'],
            # last_action_name=context_bundle['last_action'].get('tool_name'),
            last_action_documenation=tool_doc,
            # rag_context=rag_context_str,
            # rag_context_tools=rag_context_str_tools,
            tools_list=tools_list,
            result_history=result_history,
            sequence_steps=json.dumps(context_bundle['sequence_steps'], indent=4),
            last_result_params=last_result_params
            # objective=context_bundle['user_analysis_objective']
        )

        # print(prompt0)
        prompt=[prompt0,*image_prompts]
        return prompt

    def _load_prompt_templates(self) -> dict:
        """A utility function to load all .txt prompt templates from a directory."""
        templates = {}
        template_dir = "src/prompt_templates"
        for filename in os.listdir(template_dir):
            if filename.endswith(".txt"):
                template_name = filename.replace('.txt', '')
                with open(os.path.join(template_dir, filename), 'r') as f:
                    templates[template_name] = f.read()
        return templates