#!/usr/bin/env python3
"""
Test script for the deposit monitor functionality
"""
import time
from deposit_monitor import DepositMonitor
from config import Config

def test_deposit_monitor():
    """Test the deposit monitor functionality"""
    print("🧪 Testing Deposit Monitor")
    print("=" * 50)
    
    try:
        # Validate configuration first
        Config.validate_config()
        
        # Create monitor instance
        monitor = DepositMonitor(check_interval=10)  # Check every 10 seconds for testing
        
        # Show status
        status = monitor.get_status()
        print(f"📊 Monitor Status:")
        print(f"   - Running: {status['is_running']}")
        print(f"   - Check Interval: {status['check_interval']} seconds")
        print(f"   - Monitored Wallet: {status['monitored_wallet']}")
        print(f"   - Min Amount: {status['min_amount']} TON")
        print(f"   - Processed Transactions: {status['processed_transactions']}")
        print()
        
        # Start monitoring
        print("🚀 Starting monitor for 60 seconds...")
        monitor.start_monitoring()
        
        # Let it run for 60 seconds
        for i in range(6):
            time.sleep(10)
            print(f"⏰ Monitor running... ({(i+1)*10}/60 seconds)")
        
        # Stop monitoring
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        
        # Final status
        final_status = monitor.get_status()
        print(f"\n📊 Final Status:")
        print(f"   - Running: {final_status['is_running']}")
        print(f"   - Total Processed: {final_status['processed_transactions']}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(test_deposit_monitor())
