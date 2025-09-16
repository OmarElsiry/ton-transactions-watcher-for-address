#!/usr/bin/env python3
"""
Real-time Deposit Notifier - Triggers callbacks immediately when new deposits are detected
"""
import json
import time
import threading
import queue
from datetime import datetime
from typing import Set, Callable, List, Dict, Any
from dataclasses import dataclass

from config import Config
from services.transaction_service import TransactionService
from database import TransactionDB

@dataclass
class DepositEvent:
    """Represents a new deposit event"""
    wallet_address: str
    hash: str
    timestamp: str
    amount: float
    detected_at: str

class RealTimeDepositNotifier:
    """Real-time deposit notification system with callback support"""
    
    def __init__(self, check_interval: int = 10):
        self.transaction_service = TransactionService(api_type=Config.API_TYPE)
        self.db = TransactionDB()
        self.check_interval = check_interval
        self.processed_hashes: Set[str] = set()
        self.is_running = False
        self.monitor_thread = None
        
        # Event system
        self.deposit_queue = queue.Queue()
        self.callbacks: List[Callable[[DepositEvent], None]] = []
        self.latest_deposits: List[DepositEvent] = []
        self.max_latest_deposits = 50  # Keep last 50 deposits in memory
        
        # Load existing transactions to avoid duplicates
        self._load_existing_transactions()
    
    def _load_existing_transactions(self):
        """Load existing transaction hashes to avoid duplicates on startup"""
        try:
            existing_transactions = self.transaction_service.get_recent_transactions(limit=100)
            for tx in existing_transactions:
                self.processed_hashes.add(tx.hash)
            print(f"🔄 Loaded {len(self.processed_hashes)} existing transactions")
        except Exception as e:
            print(f"⚠️ Warning: Could not load existing transactions: {e}")
    
    def add_callback(self, callback: Callable[[DepositEvent], None]):
        """Add a callback function to be called when new deposits are detected"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[DepositEvent], None]):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _trigger_callbacks(self, deposit_event: DepositEvent):
        """Trigger all registered callbacks with the new deposit event"""
        for callback in self.callbacks:
            try:
                callback(deposit_event)
            except Exception as e:
                print(f"❌ Error in callback: {e}")
    
    def _check_for_new_deposits(self):
        """Check for new deposits and trigger callbacks immediately"""
        try:
            # Fetch new transactions from the blockchain
            new_transactions = self.transaction_service.fetch_new_transactions(limit=20)
            
            for transaction in new_transactions:
                # Skip if we've already processed this transaction
                if transaction.hash in self.processed_hashes:
                    continue
                
                # Only process incoming deposits (transactions with sender addresses)
                if transaction.sender_address and transaction.sender_address != Config.MONITORED_WALLET:
                    # Save transaction to database
                    tx_data = {
                        'tx_hash': transaction.hash,
                        'account_id': Config.MONITORED_WALLET,
                        'sender_address': transaction.sender_address,
                        'sender_name': getattr(transaction, 'sender_name', None),
                        'amount_ton': float(transaction.amount_ton),
                        'amount_nanoton': getattr(transaction, 'amount_nanoton', int(float(transaction.amount_ton) * 1e9)),
                        'message': getattr(transaction, 'message', ''),
                        'timestamp': getattr(transaction, 'timestamp', int(datetime.now().timestamp())),
                        'block_number': getattr(transaction, 'block_number', None),
                        'confirmed': True,
                        'processed': False,
                        'raw_data': getattr(transaction, 'raw_data', {})
                    }
                    
                    # Save to database
                    self.db.save_transaction(tx_data)
                    
                    # Update user balance (use default telegram_id if not available)
                    telegram_id = "0000000"  # Default as requested
                    self.db.create_or_update_user_balance(
                        telegram_id=telegram_id,
                        wallet_address=transaction.sender_address,
                        balance_change=float(transaction.amount_ton)
                    )
                    
                    # Create deposit event
                    deposit_event = DepositEvent(
                        wallet_address=transaction.sender_address,
                        hash=transaction.hash,
                        timestamp=transaction.formatted_time,
                        amount=float(transaction.amount_ton),
                        detected_at=datetime.now().isoformat()
                    )
                    
                    # Add to queue for API consumption
                    self.deposit_queue.put(deposit_event)
                    
                    # Add to latest deposits list
                    self.latest_deposits.append(deposit_event)
                    if len(self.latest_deposits) > self.max_latest_deposits:
                        self.latest_deposits.pop(0)  # Remove oldest
                    
                    # Trigger callbacks immediately
                    self._trigger_callbacks(deposit_event)
                    
                    # Mark as processed
                    self.processed_hashes.add(transaction.hash)
                    
                    print(f"🔔 NEW DEPOSIT DETECTED: {deposit_event.amount} TON from {deposit_event.wallet_address}")
                    print(f"💾 Transaction saved to database with hash: {transaction.hash}")
                    
        except Exception as e:
            print(f"❌ Error checking for deposits: {e}")
    
    def start_monitoring(self):
        """Start the real-time deposit monitoring"""
        if self.is_running:
            print("⚠️ Monitor is already running")
            return
        
        self.is_running = True
        print(f"🚀 Starting real-time deposit monitor...")
        print(f"👀 Monitoring wallet: {Config.MONITORED_WALLET}")
        print(f"⏱️ Check interval: {self.check_interval} seconds")
        print(f"💰 Minimum amount: {Config.MIN_AMOUNT_TON} TON")
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
        """Stop the real-time deposit monitoring"""
        if not self.is_running:
            print("⚠️ Monitor is not running")
            return
        
        print("🛑 Stopping real-time deposit monitor...")
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        print("✅ Real-time deposit monitor stopped")
    
    def get_next_deposit(self, timeout: float = None) -> DepositEvent:
        """Get the next deposit from the queue (blocking)"""
        try:
            return self.deposit_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_latest_deposits(self, limit: int = 10) -> List[DepositEvent]:
        """Get the most recent deposits from memory"""
        return self.latest_deposits[-limit:] if limit else self.latest_deposits
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitor status"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "processed_transactions": len(self.processed_hashes),
            "monitored_wallet": Config.MONITORED_WALLET,
            "min_amount": Config.MIN_AMOUNT_TON,
            "callbacks_registered": len(self.callbacks),
            "queue_size": self.deposit_queue.qsize(),
            "latest_deposits_count": len(self.latest_deposits)
        }

# Global instance for use in Flask app
realtime_notifier = RealTimeDepositNotifier(check_interval=10)

# Default callback to print to console
def console_print_callback(deposit_event: DepositEvent):
    """Default callback that prints deposits to console in JSON format"""
    deposit_json = {
        "wallet_address": deposit_event.wallet_address,
        "hash": deposit_event.hash,
        "timestamp": deposit_event.timestamp,
        "amount": deposit_event.amount
    }
    print("🔔 REAL-TIME DEPOSIT:")
    print(json.dumps(deposit_json, indent=2))
    print("-" * 50)

# Register the default console callback
realtime_notifier.add_callback(console_print_callback)
