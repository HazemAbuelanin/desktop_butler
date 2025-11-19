# DesktopButler

**A Context-Aware Desktop Automation Assistant powered by OmniLink.**

DesktopButler acts as a local bridge between the cloud-based **OmniLink AI Agent** and your **Linux Operating System**. It translates natural language voice commands into deterministic, safe operating system actions, allowing you to open applications, manage workflows, and execute system commands with a simple conversation.

## Key Features

* **Natural Language Control:** Open specific tools (e.g., "Open calculator") or URLs without memorizing terminal commands.
* **Safety First:** Dangerous commands (like closing an app) trigger a **Bidirectional Feedback Loop**, asking you for confirmation via the Agent UI before execution.
* **Decoupled Architecture:** Uses a local Flask microservice for execution and an MQTT bridge for logic, ensuring security and stability.
* **Extensible:** Easily map new applications or complex bash scripts to simple friendly names in Python.

---

## System Architecture

DesktopButler follows a 4-layer microservices pattern to bridge the gap between AI intent and local hardware execution.

| Layer | Component | Tech Stack | Role |
| :--- | :--- | :--- | :--- |
| **1. Intent** | **OmniLink Agent** | Web UI | Parses voice/text into structured templates (e.g., `open_application_code`). |
| **2. Transport** | **Mosquitto Broker** | MQTT/WebSockets | The message bus connecting the Cloud UI to your Local Machine. |
| **3. Logic** | **Bridge Script** | Python (`omnilink-lib`) | Validates commands, maps aliases (e.g., "code" $\to$ `code`), and manages safety checks. |
| **4. Execution** | **Desktop API** | Flask | A local server (Port 5001) that executes the actual `subprocess` calls to the OS. |

---

## Prerequisites

* **OS:** Linux (Tested on Ubuntu/Debian). *Easily adaptable for Mac/Windows.*
* **Python:** 3.9+
* **MQTT Broker:** Mosquitto installed and running.

### Critical Broker Configuration

Your Mosquitto broker **must** be configured to allow WebSockets on port 9001 to communicate with the OmniLink Agent.

1.  Edit your config: `sudo nano /etc/mosquitto/mosquitto.conf`
2.  Ensure these lines exist:
    ```conf
    listener 9001
    protocol websockets
    allow_anonymous true
    ```
3.  Restart broker: `sudo systemctl restart mosquitto`

---

## 📦 Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/desktop-butler.git](https://github.com/your-username/desktop-butler.git)
    cd desktop-butler
    ```

2.  **Install Dependencies:**
    This installs Flask, Requests, Paho-MQTT, and the core `omnilink-lib`.
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Usage Guide

To run DesktopButler, you need to launch the two local components.

### Step 1: Start the Execution API (Terminal 1)

This starts the local web server that listens for commands.

```bash
python desktop_api.py
# Output: Linux Desktop API running on [http://127.0.0.1:5001](http://127.0.0.1:5001)

```
Step 2: Start the OmniLink Bridge (Terminal 2)

This connects your local system to the OmniLink Agent.

```bash
python desktop_bridge.py
# Output: [OmniLinkMQTT] Connected localhost:9001 (transport=websockets)
```

Step 3: Configure OmniLink Agent

Go to the OmniLink Web UI and configure your agent to speak the correct language.

    Connection: ws://localhost:9001 (Topic: olink/commands)

    Main Task: "You are a Desktop Butler. You control local applications."

    Available Commands (Copy Exactly):

```bash
open_application_[application_name]
close_application_[application_name]
open_url_[url]
```

🎮 Examples

1. Launching an App

    You: "Open Calculator."

    Agent: Parses application_name="calculator".

    Bridge: Maps "calculator" → gnome-calculator and calls API.

    Result: Calculator window opens.

2. Safety Check (Closing)

    You: "Close VS Code."

    Bridge: Intercepts the kill command. Sends a Question back to the UI.

    Agent UI: Displays: "⚠️ Are you sure you want to force-close code?" [Yes] [Cancel]

    You: Click [Yes].

    Result: The application closes.

3. Web Navigation

    You: "Open google dot com."

    Result: Default web browser opens the URL.

🔧 Customization

To add your own apps, edit the APP_MAP dictionary in desktop_bridge.py:

```bash
APP_MAP = {
    "calculator": "gnome-calculator",
    "code": "code",
    # Add your own!
    "my-script": "bash /home/user/scripts/run_backup.sh",
    "discord": "discord"
}

```
