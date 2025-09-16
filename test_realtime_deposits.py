#!/usr/bin/env python3
"""
Test script for real-time deposit detection
"""
import time
import requests
import json
from datetime import datetime

def test_realtime_api():
    """Test the real-time deposit API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Real-Time Deposit API")
    print("=" * 50)
    
    # 1. Start real-time monitoring
    print("1. Starting real-time monitoring...")
    response = requests.post(f"{base_url}/api/deposits/realtime/start")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Real-time monitoring started")
        else:
            print(f"❌ Failed to start: {data['message']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return
    
    # 2. Check status
    print("\n2. Checking status...")
    response = requests.get(f"{base_url}/api/deposits/realtime/status")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            status = data['status']
            print(f"✅ Status: Running={status['is_running']}, Queue={status['queue_size']}")
        else:
            print(f"❌ Status check failed: {data['error']}")
    
    # 3. Wait for deposits (blocking API)
    print("\n3. Waiting for deposits (30 second timeout)...")
    print("💡 Make a test deposit to your wallet to see real-time detection!")
    
    response = requests.get(f"{base_url}/api/deposits/realtime/next?timeout=30")
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['deposit']:
            deposit = data['deposit']
            print("🔔 NEW DEPOSIT DETECTED:")
            print(json.dumps(deposit, indent=2))
        else:
            print("⏰ No deposits detected within timeout period")
    
    # 4. Stop monitoring
    print("\n4. Stopping real-time monitoring...")
    response = requests.post(f"{base_url}/api/deposits/realtime/stop")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Real-time monitoring stopped")
        else:
            print(f"❌ Failed to stop: {data['message']}")
    
    print("\n✅ Test completed!")

def test_streaming_api():
    """Test the Server-Sent Events streaming API"""
    import sseclient  # You may need to install: pip install sseclient-py
    
    base_url = "http://localhost:5000"
    
    print("🌊 Testing Streaming API")
    print("=" * 50)
    
    try:
        # Start monitoring first
        requests.post(f"{base_url}/api/deposits/realtime/start")
        
        print("📡 Connecting to deposit stream...")
        print("💡 Make a test deposit to see real-time streaming!")
        print("Press Ctrl+C to stop\n")
        
        response = requests.get(f"{base_url}/api/deposits/realtime/stream", stream=True)
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            data = json.loads(event.data)
            
            if data.get('type') == 'deposit':
                print("🔔 STREAMED DEPOSIT:")
                deposit_data = data['data']
                formatted_deposit = {
                    "wallet_address": deposit_data['wallet_address'],
                    "hash": deposit_data['hash'],
                    "timestamp": deposit_data['timestamp'],
                    "amount": deposit_data['amount']
                }
                print(json.dumps(formatted_deposit, indent=2))
                print("-" * 40)
            elif data.get('type') == 'heartbeat':
                print(f"💓 Heartbeat: {data['timestamp']}")
            elif data.get('type') == 'error':
                print(f"❌ Stream error: {data['error']}")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped by user")
    except ImportError:
        print("❌ sseclient-py not installed. Install with: pip install sseclient-py")
    except Exception as e:
        print(f"❌ Stream error: {e}")
    finally:
        # Stop monitoring
        requests.post(f"{base_url}/api/deposits/realtime/stop")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Test blocking API (recommended)")
    print("2. Test streaming API (requires sseclient-py)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_realtime_api()
    elif choice == "2":
        test_streaming_api()
    else:
        print("Invalid choice. Running blocking API test...")
        test_realtime_api()
