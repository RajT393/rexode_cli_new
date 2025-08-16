import sys
import subprocess
import os

# Conditional import for pyautogui (Windows specific)
try:
    import pyautogui
except ImportError:
    pyautogui = None

def launch_app(app_name):
    if sys.platform == "win32":
        if pyautogui is None:
            print("Error: pyautogui not installed. Please install it using 'pip install pyautogui'")
            return "Application not found or unsupported OS"
        try:
            pyautogui.press('win')
            pyautogui.write(app_name)
            pyautogui.press('enter')
            return f"Attempted to launch {app_name} on Windows."
        except Exception as e:
            return f"Error launching {app_name} on Windows: {e}"
    elif sys.platform == "darwin":  # macOS
        try:
            subprocess.run(["open", "-a", app_name], check=True)
            return f"Attempted to launch {app_name} on macOS."
        except FileNotFoundError:
            return "Application not found."
        except subprocess.CalledProcessError as e:
            return f"Error launching {app_name} on macOS: {e}"
    elif sys.platform.startswith("linux"):  # Linux
        try:
            # Try xdg-open first for broader compatibility
            subprocess.run(["xdg-open", app_name], check=True)
            return f"Attempted to launch {app_name} on Linux using xdg-open."
        except FileNotFoundError:
            # Fallback to direct execution if xdg-open is not found
            try:
                subprocess.run([app_name], check=True)
                return f"Attempted to launch {app_name} on Linux directly."
            except FileNotFoundError:
                return "Application not found."
            except subprocess.CalledProcessError as e:
                return f"Error launching {app_name} on Linux directly: {e}"
        except subprocess.CalledProcessError as e:
            return f"Error launching {app_name} on Linux using xdg-open: {e}"
    else:
        return "Unsupported operating system."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app_launcher.py <application_name>")
    else:
        app_name_to_launch = " ".join(sys.argv[1:])
        result = launch_app(app_name_to_launch)
        print(result)
