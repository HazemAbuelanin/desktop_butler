import requests
import time

# Configuration
API_URL = "http://127.0.0.1:5001"

# Linux App Names (Adjust if you are on a different OS)
CALCULATOR = "gnome-calculator" 
TEXT_EDITOR = "gedit" 

def test_open_app(app_name):
    print(f"\n🧪 TEST: Opening {app_name}...")
    try:
        # Send POST request to /open_app
        response = requests.post(
            f"{API_URL}/open_app",
            json={"app_name": app_name},
            timeout=5
        )
        
        # Check results
        if response.status_code == 200:
            print(f"✅ SUCCESS: API returned 200 OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ FAILED: API returned {response.status_code}")
            print(f"   Reason: {response.text}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: Is desktop_api.py running?")
        print(f"   Error details: {e}")

def test_close_app(app_name):
    print(f"\n🧪 TEST: Closing {app_name}...")
    try:
        response = requests.post(
            f"{API_URL}/close_app",
            json={"app_name": app_name},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: {app_name} closed.")
        else:
            print(f"⚠️ WARNING: Could not close (maybe it wasn't open?)")
            print(f"   Response: {response.json()}")

    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    print("--- Desktop API Unit Test ---")
    
    # 1. Test Open
    test_open_app(CALCULATOR)
    
    # 2. Wait a moment so you can see it open
    print("   (Waiting 3 seconds...)")
    time.sleep(3)
    
    # 3. Test Close
    test_close_app(CALCULATOR)