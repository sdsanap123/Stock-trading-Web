#!/usr/bin/env python3
"""
Run the Stock Trading App with proper configuration.
"""

import os
import sys
import subprocess

def run_app():
    """Run the Streamlit app with proper configuration."""
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Starting Stock Trading App...")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("Error: app.py not found!")
        return
    
    # Run streamlit with file watcher disabled
    try:
        cmd = [
            "streamlit", "run", "app.py",
            "--server.fileWatcherType", "none",
            "--server.runOnSave", "false",
            "--server.headless", "false",
            "--server.port", "8501"
        ]
        
        print("Running command:", " ".join(cmd))
        print("\nApp will open at: http://localhost:8501")
        print("Press Ctrl+C to stop the app\n")
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running app: {e}")
    except KeyboardInterrupt:
        print("\nApp stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_app()
