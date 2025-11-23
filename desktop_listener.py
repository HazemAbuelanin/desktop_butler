import paho.mqtt.client as mqtt
import json

# --- Configuration from your Screenshot ---
BROKER    = "localhost"
PORT      = 9001
TRANSPORT = "websockets"

# Topics defined in OmniLink UI
TOPIC_COMMANDS  = "olink/commands"
TOPIC_FEEDBACK  = "olink/commands_feedback"
TOPIC_CONTEXT   = "olink/context"
TOPIC_INLINE    = "olink/inline_code"

# We subscribe to the wildcard to catch ALL of them
WILDCARD_TOPIC  = "olink/#"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ CONNECTED to Broker ({BROKER}:{PORT})")
        print(f"   Transport: {TRANSPORT}")
        print(f"📡 Listening for:")
        print(f"   - Commands: {TOPIC_COMMANDS}")
        print(f"   - Feedback: {TOPIC_FEEDBACK}")
        print("-" * 40)
        print("Waiting for activity... (Speak to the Agent now)")
        client.subscribe(WILDCARD_TOPIC)
    else:
        print(f"❌ Connection Failed. Result Code: {rc}")
        if rc == 5:
            print("   (RC=5 means Authorization Error. Check 'allow_anonymous true' in mosquitto.conf)")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        topic = msg.topic
        
        print("\n" + "=" * 40)
        
        # Identify the Message Type based on your Screenshot
        if topic == TOPIC_COMMANDS:
            print(f"📥 TYPE: COMMAND (Agent -> Bridge)")
        elif topic == TOPIC_FEEDBACK:
            print(f"📤 TYPE: FEEDBACK (Bridge -> Agent)")
        elif topic == TOPIC_CONTEXT:
            print(f"ℹ️ TYPE: CONTEXT UPDATE")
        elif topic == TOPIC_INLINE:
            print(f"💻 TYPE: INLINE CODE")
        else:
            print(f"❓ TYPE: UNKNOWN TOPIC")

        print(f"📍 Topic:   {topic}")
        
        # Pretty Print JSON
        try:
            data = json.loads(payload)
            print(f"📦 Payload:\n{json.dumps(data, indent=2)}")
        except:
            print(f"📦 Payload: {payload}")
            
    except Exception as e:
        print(f"Error decoding message: {e}")

# Initialize Client
client = mqtt.Client(transport=TRANSPORT)
client.on_connect = on_connect
client.on_message = on_message

print("--- OmniLink Traffic Sniffer ---")
try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except ConnectionRefusedError:
    print(f"❌ ERROR: Could not connect to {BROKER}:{PORT}.")
    print("   Is Mosquitto running? (sudo systemctl start mosquitto)")