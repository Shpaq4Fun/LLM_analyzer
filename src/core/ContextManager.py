from datetime import datetime

class ContextManager:
    def __init__(self):
        self.conversation_history = []
        self.semantic_memory = {}      # Learned patterns
        self.episodic_memory = []      # Time-ordered events
        self.working_memory = []       # Current session state
        self.variable_registry = {}    # Variable states
        self.max_context_length = 50000
    
    def add_interaction(self, prompt, response, metadata):
        """Add interaction to conversation history"""
        history_entry = {
            'timestamp': datetime.now(),
            'step_number': metadata.get('step_number'),
            'interaction_type': metadata.get('interaction_type'),
            'prompt': prompt,
            'response': response,
            'metadata': metadata
        }
        self.conversation_history.append(history_entry)

    def build_context(self, context_type, current_task):
        """Build contextual prompt for LLM"""
        formatted_context = self._format_context(self.conversation_history)
        
        # For now, we'll just prepend the context to the current task prompt.
        # This can be made more sophisticated later.
        return f"--- CONTEXT: ---\n\n{formatted_context}\n\n--- END OF CONTEXT ---\n\n{current_task}"

    def _format_context(self, conversation_history):
        """Formats conversation history into a string for the prompt."""
        if not conversation_history:
            return "No conversation history yet."
        
        formatted_history = []
        for entry in conversation_history:
            formatted_history.append(f"On {entry['timestamp']}, the following interaction occurred:")
            formatted_history.append(f"Prompt: {entry['prompt']}")
            formatted_history.append(f"Response: {entry['response']}")
            formatted_history.append("-" * 20)
            
        return "\n".join(formatted_history)
