import os
import google.generativeai as genai

# Ustaw zmienną środowiskową, aby wskazywała na Twój plik z kluczem JSON
# Zastąp ścieżkę swoją własną ścieżką do pliku
def get_credentials():

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "D:\\Drive\\Projekty\\LLM_analyzer\\src\\core\\llm-analyzer-466009-81c353112c07.json"

    # Teraz możesz normalnie korzystać z biblioteki.
    # Nie potrzebujesz już genai.configure(api_key=...).
    # Biblioteka automatycznie znajdzie i użyje Twojego pliku z kluczem.
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # response = model.generate_content("Test")
        # print("API call successful!")
        # print(response.text)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False