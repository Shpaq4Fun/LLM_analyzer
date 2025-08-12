"""
Application entry point for AIDA (AI-Driven Analyzer).

- Prints basic environment info (working directory and Python path) for debugging
- Imports the Tkinter-based GUI App and a credentials check helper
- Starts the GUI if credentials are available; otherwise exits gracefully
"""

import os
import sys

print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Path: {sys.path}")

from src.gui.main_window import App
from src.core.authentication import get_credentials

if __name__ == "__main__":
    if get_credentials():
        app = App()
        app.mainloop()
    else:
        print("Authentication failed. Exiting application.")
