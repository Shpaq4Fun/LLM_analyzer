"""
Authentication and credentials helper for Google Generative AI.

- Sets environment variables so the Google SDK can locate service account credentials
- Performs a lightweight model instantiation to validate that credentials are usable
- Returns True on success, False otherwise

Note: The JSON key path is currently hardcoded for local development. Replace it with your own path.
"""

import os
import google.generativeai as genai
# from google import genai
# Set the environment variable to point to your JSON key file
# Replace the path with your own local path
def get_credentials():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "D:\\Drive\\Projekty\\LLM_analyzer\\src\\core\\llm-analyzer-466009-81c353112c07.json"

    # You can now normally use the library.
    # You no longer need to call genai.configure(api_key=...).
    # The library will automatically find and use your key file.
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False