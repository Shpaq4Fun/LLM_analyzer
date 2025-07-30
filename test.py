import json
import re

def extract_text_and_json(response_string):
    """
    Extracts the text description and a JSON object from a Gemini API response string.

    Args:
        response_string (str): The raw string response from the Gemini API,
                               containing text followed by a JSON object.

    Returns:
        tuple: A tuple containing two elements:
               - str: The text description part.
               - dict or None: The parsed JSON object as a dictionary, or None if
                               no valid JSON object is found.
    """
    # 1. Try to find the start of a JSON object using regex
    # We use a non-greedy match (.*?) to find the first '{'
    # and then capture everything until the last '}'
    # re.DOTALL makes '.' match newlines as well
    match = re.search(r'(.*?)\s*{[^{}]*(?:{[^{}]*}[^{}]*)*}(?:[^{}]*)$', response_string, re.DOTALL)

    if match:
        text_part = match.group(1).strip() # Get the text before the JSON, strip whitespace
        json_string_raw = match.group(0)[len(text_part):].strip() # Get the full JSON part including curly braces

        # Clean up common issues from LLM-generated JSON (e.g., unicode non-breaking space)
        # The example has a non-breaking space (U+00A0) which needs to be replaced
        json_string_clean = json_string_raw.replace('\u00A0', ' ').strip()

        try:
            # Attempt to parse the cleaned JSON string
            json_object = json.loads(json_string_clean)
            return text_part, json_object
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to decode JSON part: {e}")
            print(f"Problematic JSON string: '{json_string_clean}'")
            return response_string.strip(), None # Return original string if JSON fails
    else:
        # If no JSON object is found, return the whole string as text
        return response_string.strip(), None

# Your provided response string
gemini_response = 'The initial time series data has been loaded and visualized. The plot shows some impulsive behavior, confirming the initial hypothesis. To further investigate the frequency content and identify potential carrier frequencies, a spectrogram is recommended.\n\n\n{  \n    "action_id": 1,  \n    "tool_name": "create_signal_spectrogram",  \n    "params": {  \n        "signal_data": "loaded_signal[\'signal_data\']",  \n        "sampling_rate": "loaded_signal[\'sampling_rate\']",  \n        "output_image_path": "./run_state/run_20250723_122457\\\\step1_spectrogram.png"  \n    },  \n    "output_variable": "spectrogram"  \n}\n'

# Use the method
text_description, json_data = extract_text_and_json(gemini_response)

print("--- Text Description ---")
print(text_description)
print("\n--- JSON Data ---")
if json_data:
    print(json.dumps(json_data, indent=2))
else:
    print("No valid JSON found or could not be parsed.")

# --- Test with only text ---
print("\n--- Test with only text ---")
only_text_response = "This is just some plain text response."
text_only, json_only = extract_text_and_json(only_text_response)
print("Text:", text_only)
print("JSON:", json_only)

# --- Test with malformed JSON (to show error handling) ---
print("\n--- Test with malformed JSON ---")
malformed_json_response = "Some text.\n{\n\"key\": \"value\",\n\"malformed\n}"
text_malformed, json_malformed = extract_text_and_json(malformed_json_response)
print("Text:", text_malformed)
print("JSON:", json_malformed) # Should be None