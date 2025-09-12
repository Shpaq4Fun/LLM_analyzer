import sys
import os

print("Testing VSCode Run Button Configuration")
print("=" * 40)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Check if we're using the virtual environment
if "venv" in sys.executable:
    print("✓ Using virtual environment")
else:
    print("✗ Not using virtual environment")

# Check if we can import packages from the virtual environment
try:
    import customtkinter
    print("✓ Successfully imported customtkinter (from venv)")
except ImportError:
    print("✗ Failed to import customtkinter")

try:
    import numpy
    print("✓ Successfully imported numpy (from venv)")
except ImportError:
    print("✗ Failed to import numpy")

print("\nIf you see checkmarks above, the VSCode run button is properly configured!")
print("You can now delete this test file.")
