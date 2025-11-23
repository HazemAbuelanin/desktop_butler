import paho.mqtt.client as mqtt
import json
import time

# --- Configuration ---
# Matches your setup exactly
BROKER    = "localhost"
PORT      = 9001
TRANSPORT = "websockets"
TOPIC     = "olink/commands"

# The Fake Command to send
FAKE_PAYLOAD = {
    "template": "open_application_[application_name]",
    "vars": {
        "application_name": "calculator"
    }
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Publisher Connected to {BROKER}:{PORT}")
        
        # Convert dict to JSON string
        msg = json.dumps(FAKE_PAYLOAD)
        
        print(f"🚀 Publishing to '{TOPIC}'...")
        client.publish(TOPIC, msg)
        
        print("✅ Message Sent!")
        # Wait a tiny bit to ensure network transmission, then exit
        time.sleep(1)
        client.disconnect()
    else:
        print(f"❌ Connection Failed. Result Code: {rc}")

# Initialize Client
client = mqtt.Client(transport=TRANSPORT)
client.on_connect = on_connect

print("--- OmniLink Test Publisher ---")
try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except ConnectionRefusedError:
    print(f"❌ ERROR: Could not connect to {BROKER}:{PORT}.")
    print("   Make sure Mosquitto is running.")
except KeyboardInterrupt:
    pass