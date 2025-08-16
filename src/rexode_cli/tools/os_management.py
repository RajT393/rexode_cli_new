import os
import subprocess
import shutil
import zipfile
import platform

def open_application(application_name):
    """Opens an application on the user's operating system."""
    try:
        if platform.system() == 'Windows':
            os.startfile(application_name)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', '-a', application_name])
        elif platform.system() == 'Linux':  # Linux
            subprocess.call(['xdg-open', application_name])
        else:
            return f"Unsupported operating system: {platform.system()}"
        return f"Successfully opened {application_name}"
    except Exception as e:
        return f"Error opening application: {e}"

def list_files(path):
    """Lists all files and directories in a given path."""
    try:
        return os.listdir(path)
    except Exception as e:
        return f"Error listing files: {e}"

def read_file(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(file_path, content):
    """Writes content to a file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {e}"

def delete_file(file_path):
    """Deletes a file."""
    try:
        os.remove(file_path)
        return f"Successfully deleted {file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"

def move_file(source_path, destination_path):
    """Moves a file from a source path to a destination path."""
    try:
        shutil.move(source_path, destination_path)
        return f"Successfully moved {source_path} to {destination_path}"
    except Exception as e:
        return f"Error moving file: {e}"

def compress_files(file_paths, archive_path):
    """Compresses files into a zip archive."""
    try:
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for file_path in file_paths:
                zipf.write(file_path, os.path.basename(file_path))
        return f"Successfully compressed files to {archive_path}"
    except Exception as e:
        return f"Error compressing files: {e}"

def extract_archive(archive_path, extract_path):
    """Extracts files from a zip archive."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_path)
        return f"Successfully extracted archive to {extract_path}"
    except Exception as e:
        return f"Error extracting archive: {e}"

def system_info():
    """Gets information about the user's system."""
    try:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    except Exception as e:
        return f"Error getting system info: {e}"

def execute_shell_command(command):
    """Executes a shell command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return f"Error executing shell command: {e}"
