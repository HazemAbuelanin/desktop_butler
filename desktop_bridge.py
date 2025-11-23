import requests
import time
import json
import os
import logging
import sys

# --- CONFIGURATION ---
MQTT_HOST = "127.0.0.1" 
MQTT_PORT = 9001
API_URL   = "http://127.0.0.1:5001"

# Force Topics
os.environ["MQTT_COMMAND_TOPIC"] = "olink/commands"
os.environ["MQTT_FEEDBACK_TOPIC"] = "olink/commands_feedback"

# We use the library for Connection & Feedback, but we will override the parsing
from omnilink import OmniLinkEngine, OmniLinkMQTTBridge, AgentFeedback

APP_MAP = {
    "calculator": "gnome-calculator", 
    "code": "code",                  
    "terminal": "gnome-terminal",
    "files": "nautilus",             
    "browser": "firefox",
    "spotify": "spotify",            
    "editor": "gedit"                
}

# --- LOGIC HANDLER ---
def process_command_logic(command_str, bridge_instance):
    """
    Decides what to do based on the clean command string.
    """
    print(f"🧠 LOGIC: Processing '{command_str}'")
    
    # NOTE: We create a temporary messenger object to send feedback
    # The library usually does this, but we are doing it manually now.
    class SimpleMessenger:
        def send_feedback(self, feedback_obj):
            # Manually publish feedback to the topic
            payload = json.dumps(feedback_obj.to_dict())
            bridge_instance.client.publish(os.environ["MQTT_FEEDBACK_TOPIC"], payload)
            print(f"📤 FEEDBACK SENT: {payload}")

    messenger = SimpleMessenger()

    # --- ROUTE: OPEN ---
    if command_str.startswith("open_application_"):
        app_alias = command_str.replace("open_application_", "").strip()
        print(f"🚩 ACTION: OPEN '{app_alias}'")
        
        target_cmd = APP_MAP.get(app_alias.lower())
        if not target_cmd:
            print(f"❌ ERROR: No mapping for '{app_alias}'")
            messenger.send_feedback(AgentFeedback(f"No mapping for '{app_alias}'"))
            return

        messenger.send_feedback(AgentFeedback(f"Launching {app_alias}..."))
        
        try:
            requests.post(f"{API_URL}/open_app", json={"app_name": target_cmd}, timeout=2)
            print(f"✅ API SUCCESS")
        except Exception as e:
            print(f"❌ API ERROR: {e}")

    # --- ROUTE: CLOSE ---
    elif command_str.startswith("close_application_"):
        app_alias = command_str.replace("close_application_", "").strip()
        print(f"🚩 ACTION: CLOSE '{app_alias}'")
        
        target_cmd = APP_MAP.get(app_alias.lower())
        if not target_cmd: return

        messenger.send_feedback(AgentFeedback(f"Closing {app_alias}..."))
        try:
            requests.post(f"{API_URL}/close_app", json={"app_name": target_cmd})
            print(f"✅ API SUCCESS")
        except Exception as e:
            print(f"❌ API ERROR: {e}")

# --- CUSTOM MESSAGE PROCESSOR ---
def on_mqtt_message(client, userdata, msg):
    """
    This replaces the library's default handler. 
    It parses JSON and calls our logic directly.
    """
    try:
        payload = msg.payload.decode()
        print("\n" + "="*40)
        print(f"📥 RECEIVED RAW: {payload}")
        
        # 1. Parse JSON
        data = json.loads(payload)
        
        # 2. Extract Command
        command_str = data.get("command")
        
        if command_str:
            print(f"✅ EXTRACTED COMMAND: {command_str}")
            # 3. Run Logic
            process_command_logic(command_str, userdata['bridge'])
        else:
            print("⚠️ JSON valid, but no 'command' field.")
            
    except json.JSONDecodeError:
        print("⚠️ Not JSON. Ignoring.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR processing message: {e}")

# --- SETUP ---
engine = OmniLinkEngine([]) 

print("--- DesktopButler Bridge (Custom Parser) ---")
print(f"Target: {MQTT_HOST}:{MQTT_PORT}")

# Initialize Bridge
bridge = OmniLinkMQTTBridge(
    engine, 
    host=MQTT_HOST, 
    port=MQTT_PORT, 
    transport="websockets"
)

# --- THE OVERRIDE ---
# We inject our custom handler into the Paho client
# We pass the 'bridge' object in userdata so the handler can send feedback
bridge.client.user_data_set({'bridge': bridge})
bridge.client.on_message = on_mqtt_message
# --------------------

if __name__ == "__main__":
    bridge.start()
    # We must manually subscribe because we overrode the start sequence logic behavior
    # Wait a moment for connection then subscribe
    time.sleep(1) 
    print(f"🔌 Subscribing to {os.environ['MQTT_COMMAND_TOPIC']}...")
    bridge.client.subscribe(os.environ["MQTT_COMMAND_TOPIC"])
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()