"""
Redirect to the actual Streamlit app
This file exists only to satisfy Streamlit Cloud's main module requirement
"""
import subprocess
import sys

# Run the actual app
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
