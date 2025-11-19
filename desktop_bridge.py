import requests
import time
from omnilink import OmniLinkEngine, OmniLinkMQTTBridge, AgentFeedback

# Where to send the final commands (Point to the API file above)
DESKTOP_API_URL = "http://127.0.0.1:5001"

# --- THE MAPPING (The "Context") ---
# The AI sends "calculator". Linux needs "gnome-calculator".
# This dictionary bridges the gap between human speech and computer requirements.
APP_MAP = {
    "calculator": "gnome-calculator",
    "code": "code",
    "browser": "firefox",
    # Add more here!
}

# Helper function to look up the map
def get_linux_command(app_alias):
    return APP_MAP.get(app_alias.lower())

# --- HANDLER 1: OPENING APPLICATION ---
def handle_open_app(event: dict):
    # 'event' contains everything the AI sent
    messenger = event.get("messenger") # Tool to talk back to the user
    
    # 1. Extract the variable from the template: open_application_[application_name]
    app_alias = event["vars"].get("application_name", "").lower()
    
    # 2. Map "calculator" -> "gnome-calculator"
    target_cmd = get_linux_command(app_alias)

    if not target_cmd:
        # Tell the user we don't know this app yet
        if messenger:
            messenger.send_feedback(AgentFeedback(f"I don't have a mapping for '{app_alias}'."))
        return

    # 3. Send "Feedback" to the UI (User sees "Launching calculator...")
    if messenger:
        messenger.send_feedback(AgentFeedback(f"Launching {app_alias} ({target_cmd})..."))

    # 4. Send the HTTP Request to desktop_api.py
    try:
        requests.post(f"{DESKTOP_API_URL}/open_app", json={"app_name": target_cmd})
    except Exception as e:
        print(f"API Connection Error: {e}")

# --- HANDLER 2: CLOSING (With Safety) ---
def handle_close_app(event: dict):
    messenger = event.get("messenger")
    # 1. Extract the variable from the template: close_application_[application_name]
    app_alias = event["vars"].get("application_name", "").lower()
    # 2. Map the app alias to the target command
    target_cmd = get_linux_command(app_alias)

    if not target_cmd:
        if messenger:
            messenger.send_feedback(AgentFeedback(f"I don't have a mapping for '{app_alias}' to close."))
        return

    # --- THE SAFETY CHECK ---
    if messenger:
        # 1. Ask the Question
        question_text = f"⚠️ Safety Check: Are you sure you want to kill '{app_alias}'?"
        
        # 2. PAUSE execution and wait for the user to click a button in the UI
        reply = messenger.ask_question(question_text, choices=["Yes, kill it", "Cancel"]).wait(timeout=30)
        
        # 3. Check the answer
        if reply and reply.get("answer") == "Yes, kill it":
            messenger.send_feedback(AgentFeedback(f"Terminating {app_alias}..."))
            # 4. Only NOW do we send the request to the API
            try:
                requests.post(f"{DESKTOP_API_URL}/close_app", json={"app_name": target_cmd})
            except Exception as e:
                print(f"API Connection Error: {e}")
        else:
            messenger.send_feedback(AgentFeedback("Action cancelled."))

# --- HANDLER 3: OPENING URL (NEW) ---
def handle_open_url(event: dict):
    messenger = event.get("messenger")
    
    # 1. Extract the URL from the template: open_url_[url]
    url = event["vars"].get("url", "")
    
    if not url:
        if messenger:
            messenger.send_feedback(AgentFeedback("No URL provided to open."))
        return

    # 2. Send "Feedback" to the UI
    if messenger:
        messenger.send_feedback(AgentFeedback(f"Opening URL: {url}..."))

    # 3. Send the HTTP Request to desktop_api.py
    try:
        # This assumes your desktop_api.py has a /open_url endpoint that handles this
        requests.post(f"{DESKTOP_API_URL}/open_url", json={"url": url})
    except Exception as e:
        print(f"API Connection Error: {e}")


# --- STARTUP SEQUENCE ---
engine = OmniLinkEngine([]) # Create the brain

# Teach the brain the templates
engine.on_template("open_application_[application_name]", handle_open_app)
engine.on_template("close_application_[application_name]", handle_close_app)
engine.on_template("open_url_[url]", handle_open_url)

# Connect the ears (WebSockets, Port 9001)
bridge = OmniLinkMQTTBridge(engine, host="localhost", port=9001, transport="websockets")

if __name__ == "__main__":
    bridge.start() # Start the background thread
    
    # Keep the main script running forever so the bridge doesn't die
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()