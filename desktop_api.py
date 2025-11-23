import subprocess
import webbrowser
import os
import sys
from flask import Flask, request

app = Flask(__name__)

def run_linux_command(command_list):
    """Helper to run Linux commands safely detached."""
    try:
        # setsid is crucial on Linux/Ubuntu to detach the process from the terminal
        subprocess.Popen(command_list, start_new_session=True)
        return True, None
    except Exception as e:
        return False, str(e)

@app.route("/open_app", methods=['POST'])
def open_app():
    data = request.json
    app_name = data.get('app_name')
    
    print(f"\n🚩 API FLAG: Received request to OPEN -> {app_name}")

    if not app_name:
        return {"status": "error", "message": "app_name missing"}, 400

    success, error = run_linux_command([app_name])
    
    if success:
        print(f"✅ API SUCCESS: {app_name} launched.")
        return {"status": "success", "command": f"opened {app_name}"}, 200
    else:
        print(f"❌ API ERROR: Failed to open {app_name}. Reason: {error}")
        return {"status": "error", "message": error}, 500

@app.route("/close_app", methods=['POST'])
def close_app():
    data = request.json
    app_name = data.get('app_name')

    print(f"\n🚩 API FLAG: Received request to CLOSE -> {app_name}")

    if not app_name:
        return {"status": "error", "message": "app_name missing"}, 400

    try:
        # pkill -f is standard on Ubuntu for finding processes by name
        subprocess.run(["pkill", "-f", app_name], check=True)
        print(f"✅ API SUCCESS: {app_name} terminated.")
        return {"status": "success", "command": f"killed {app_name}"}, 200
    except subprocess.CalledProcessError:
        print(f"⚠️ API WARNING: Could not find process {app_name} to kill.")
        return {"status": "error", "message": "Process not found."}, 404
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route("/open_url", methods=['POST'])
def open_url():
    url = request.json.get('url')
    print(f"\n🚩 API FLAG: Received request to OPEN URL -> {url}")
    
    if not url: return {"status": "error", "message": "url missing"}, 400
    
    try:
        webbrowser.open(url)
        print(f"✅ API SUCCESS: Browser triggered for {url}")
        return {"status": "success"}, 200
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    print("--- Ubuntu Desktop API Initialized ---")
    print("🚩 Waiting for commands on port 5001...")
    app.run(port=5001)