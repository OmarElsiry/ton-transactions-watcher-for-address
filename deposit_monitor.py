#!/usr/bin/env python3
"""
TON Deposit Monitor - Real-time deposit detection with JSON output
Continuously monitors for new deposits and prints them in JSON format
"""
import json
import time
import threading
from datetime import datetime
from typing import Set

from config import Config
from services.transaction_service import TransactionService

class DepositMonitor:
    """Real-time deposit monitor with JSON output"""
    
    def __init__(self, check_interval: int = 30):
        self.transaction_service = TransactionService(api_type=Config.API_TYPE)
        self.check_interval = check_interval
        self.processed_hashes: Set[str] = set()
        self.is_running = False
        self.monitor_thread = None
        
        # Load existing transaction hashes to avoid duplicates on startup
        self._load_existing_transactions()
    
    def _load_existing_transactions(self):
        """Load existing transaction hashes to avoid printing duplicates on startup"""
        try:
            existing_transactions = self.transaction_service.get_recent_transactions(limit=100)
            for tx in existing_transactions:
                self.processed_hashes.add(tx.tx_hash)
            print(f"📋 Loaded {len(self.processed_hashes)} existing transactions to avoid duplicates")
        except Exception as e:
            print(f"⚠️ Warning: Could not load existing transactions: {e}")
    
    def _format_deposit_json(self, transaction) -> str:
        """Format transaction as JSON with the requested fields"""
        deposit_data = {
            "wallet_address": transaction.sender_address,
            "hash": transaction.tx_hash,
            "timestamp": transaction.timestamp,
            "amount": float(transaction.amount_ton)
        }
        return json.dumps(deposit_data, indent=2)
    
    def _check_for_new_deposits(self):
        """Check for new deposits and print them in JSON format"""
        try:
            # Fetch new transactions from the blockchain
            new_transactions = self.transaction_service.fetch_new_transactions(limit=20)
            
            for transaction in new_transactions:
                # Skip if we've already processed this transaction
                if transaction.tx_hash in self.processed_hashes:
                    continue
                
                # Only process incoming deposits (transactions with sender addresses)
                if transaction.sender_address and transaction.sender_address != Config.MONITORED_WALLET:
                    # Print deposit in JSON format
                    print("🔔 NEW DEPOSIT DETECTED:")
                    print(self._format_deposit_json(transaction))
                    print("-" * 50)
                    
                    # Mark as processed
                    self.processed_hashes.add(transaction.tx_hash)
                    
        except Exception as e:
            print(f"❌ Error checking for deposits: {e}")
    
    def start_monitoring(self):
        """Start the deposit monitoring loop"""
        if self.is_running:
            print("⚠️ Monitor is already running")
            return
        
        self.is_running = True
        print(f"🚀 Starting deposit monitor...")
        print(f"👀 Monitoring wallet: {Config.MONITORED_WALLET}")
        print(f"⏱️ Check interval: {self.check_interval} seconds")
        print(f"💰 Minimum amount: {Config.MIN_AMOUNT_TON} TON")
        print(f"🔄 Using API: {Config.API_TYPE}")
        print("=" * 60)
        
        def monitor_loop():
            while self.is_running:
                try:
                    self._check_for_new_deposits()
                    time.sleep(self.check_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Monitor error: {e}")
                    time.sleep(self.check_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the deposit monitoring"""
        if not self.is_running:
            print("⚠️ Monitor is not running")
            return
        
        print("🛑 Stopping deposit monitor...")
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        print("✅ Deposit monitor stopped")
    
    def get_status(self) -> dict:
        """Get current monitor status"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "processed_transactions": len(self.processed_hashes),
            "monitored_wallet": Config.MONITORED_WALLET,
            "min_amount": Config.MIN_AMOUNT_TON
        }

def main():
    """Main function to run the deposit monitor"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Create and start monitor
        monitor = DepositMonitor(check_interval=30)  # Check every 30 seconds
        monitor.start_monitoring()
        
        print("💡 Monitor is running. Press Ctrl+C to stop.")
        print("📊 Status updates will appear below:")
        print()
        
        # Keep the main thread alive
        try:
            while monitor.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received stop signal...")
            monitor.stop_monitoring()
            
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
