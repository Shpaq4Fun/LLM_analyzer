import subprocess
import os

def authenticate_gemini():
    """
    Authenticates with the Gemini CLI using gcloud auth application-default login.
    """
    gcloud_path = None
    try:
        # Check if gcloud is installed and in PATH
        try:
            subprocess.run(["gcloud", "--version"], check=True, capture_output=True)
            gcloud_path = "gcloud"  # Use gcloud from PATH
        except FileNotFoundError:
            # Attempt to locate gcloud in common installation directories
            for path in ["C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd",
                         "C:\\Program Files\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd",
                         "C:\\Users\\JW\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"]:
                if os.path.exists(path):
                    gcloud_path = path
                    break

            if not gcloud_path:
                print("Error: gcloud CLI is not installed or not in your system's PATH.")
                print("Please ensure that the Google Cloud SDK is installed and that the 'gcloud' command is added to your system's PATH environment variable.")
                print("Follow the instructions here: https://cloud.google.com/sdk/docs/install")
                print("After installation and PATH configuration, run 'gcloud init' to initialize the gcloud CLI.")
                return False

        # Check if the user is already authenticated
        result = subprocess.run([gcloud_path, "auth", "application-default", "print-access-token"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Gemini CLI is already authenticated.")
            return True  # Already authenticated

        # Authenticate with gcloud
        print("Authenticating with Gemini CLI...")
        # Use the correct scope for the Generative Language API
        scopes = "https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever"
        subprocess.run([gcloud_path, "auth", "application-default", "login", f"--scopes={scopes}"], check=True)
        # subprocess.run([gcloud_path, "auth", "application-default", "login", "--scopes=https://www.googleapis.com/auth/cloud-platform"], check=True)
        print("Gemini CLI authentication successful.")
        return True

    except subprocess.CalledProcessError as e:
        if "Your current project has not been set" in str(e.stderr):
            print("Please run 'gcloud init' to initialize the gcloud CLI.")
            return False
        print(f"Error during Gemini CLI authentication: {e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if authenticate_gemini():
        print("Authentication check passed.")
    else:
        print("Authentication check failed.")
