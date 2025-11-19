import subprocess  # Allows Python to run Linux terminal commands (like 'ls', 'pkill')
import webbrowser  # A built-in Python tool to open URLs in the default browser
from flask import Flask, request # The web server framework

app = Flask(__name__)

# --- ENDPOINT 1: OPENING APPS ---
@app.route("/open_app", methods=['POST'])
def open_app():
    # 1. Get the data sent from the bridge
    data = request.json 
    app_name = data.get('app_name') # e.g., "gnome-calculator"
    
    # 2. Validation: Did we actually get a name?
    if not app_name:
        return {"status": "error", "message": "app_name missing"}, 400

    try:
        print(f"Executing: {app_name}")
        
        # 3. The Critical Line:
        # subprocess.Popen: Starts the app.
        subprocess.Popen(app_name, shell=True, start_new_session=True)
        
        return {"status": "success", "command": f"opened {app_name}"}, 200
    except Exception as e:
        # Pylance fix: Added the required 'except' block.
        print(f"Error opening application {app_name}: {e}")
        return {"status": "error", "message": f"Could not open application: {e}"}, 500

# --- ENDPOINT 2: CLOSING APPS ---
@app.route("/close_app", methods=['POST'])
def close_app():
    # Pylance fix: Variable 'app_name' was not defined/extracted here.
    data = request.json 
    app_name = data.get('app_name') # e.g., "gnome-calculator"

    # Validation
    if not app_name:
        return {"status": "error", "message": "app_name missing"}, 400
    
    try:
        print(f"Closing process matching: {app_name}")
        
        # 4. The Killer Command:
        # "pkill -f": A Linux command that finds a process by name and kills it.
        subprocess.run(["pkill", "-f", app_name], check=True)
        
        return {"status": "success", "command": f"killed {app_name}"}, 200
    except subprocess.CalledProcessError as e:
        # Pylance fix: Added the required 'except' block. Specific exception for 'pkill' failure.
        print(f"Process not found or could not be killed: {e}")
        return {"status": "error", "message": f"Process '{app_name}' not found or could not be killed."}, 404
    except Exception as e:
        print(f"Error closing process {app_name}: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}, 500

# --- ENDPOINT 3: OPENING URL ---
@app.route("/open_url", methods=['POST'])
def open_url():
    data = request.json
    url = data.get('url')

    if not url:
        return {"status": "error", "message": "url missing"}, 400

    try:
        print(f"Opening URL: {url}")
        webbrowser.open(url)
        return {"status": "success", "command": f"opened URL {url}"}, 200
    except Exception as e:
        # Pylance fix: Added the required 'except' block.
        print(f"Error opening URL {url}: {e}")
        return {"status": "error", "message": f"Could not open URL: {e}"}, 500

if __name__ == '__main__':
    # 5. Start the local server on Port 5001
    app.run(port=5001)