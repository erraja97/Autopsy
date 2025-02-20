import sys, os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    In development, relative_path is used as-is.
    In a bundled exe, adjust paths that start with "autopsy/".
    """
    try:
        base_path = sys._MEIPASS
        # If running as a bundled app, remove "autopsy/" from the path if present.
        if relative_path.startswith("autopsy/"):
            relative_path = relative_path[len("autopsy/"):]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
