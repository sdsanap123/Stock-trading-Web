#!/usr/bin/env python3
"""
Fix Streamlit file watcher issues.
"""

import os
import sys
import time

def fix_streamlit_watcher():
    """Fix common Streamlit file watcher issues."""
    
    print("Fixing Streamlit file watcher issues...")
    
    # Check current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Check if we're in the correct directory
    if not os.path.exists("app.py"):
        print("Error: app.py not found in current directory")
        print("Please run this script from the Stock trading Web directory")
        return
    
    # Clean up any problematic files
    problematic_files = [
        ".streamlit/watcher_state.json",
        ".streamlit/cache",
        "__pycache__",
        ".pytest_cache"
    ]
    
    for file_path in problematic_files:
        if os.path.exists(file_path):
            try:
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"Removed directory: {file_path}")
                else:
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
    
    # Create a clean .streamlit directory
    os.makedirs(".streamlit", exist_ok=True)
    
    # Update .streamlit/config.toml to disable file watcher
    config_path = ".streamlit/config.toml"
    config_content = """[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#1f4e79"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"

[browser]
gatherUsageStats = false

[logger]
level = "info"

[client]
caching = false
"""

    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"Updated {config_path}")
    except Exception as e:
        print(f"Error updating config: {e}")
    
    print("\nStreamlit watcher fix completed!")
    print("\nTo run the app:")
    print("1. streamlit run app.py --server.fileWatcherType none")
    print("2. Or: streamlit run app.py --server.runOnSave false")
    print("\nAlternative: Use the run_app.py script")

if __name__ == "__main__":
    fix_streamlit_watcher()
