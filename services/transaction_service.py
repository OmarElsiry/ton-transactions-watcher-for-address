from typing import List, Optional, Dict, Any
from datetime import datetime

from database import TransactionDB
from models.transaction import Transaction
from services.api_client import TonCenterAPI, TonAPIFree, APIClientFactory
from utils.helpers import ValidationHelper, PerformanceHelper
from config import Config

class TransactionService:
    """Service layer for transaction operations"""
    
    def __init__(self, api_type: str = "toncenter"):
        self.api_client = APIClientFactory.create_client(api_type)
        self.db = TransactionDB()
        self.monitored_wallet = Config.MONITORED_WALLET
        self.min_amount = Config.MIN_AMOUNT_TON
    
    def fetch_new_transactions(self, limit: int = 10) -> List[Transaction]:
        """Fetch new transactions from API and save to database"""
        try:
            # Get transactions from API
            transactions = self.api_client.get_transactions(self.monitored_wallet, limit)
            
            new_transactions = []
            for tx in transactions:
                # Filter by minimum amount
                if tx.amount_ton < self.min_amount:
                    continue
                
                # Only process incoming transactions (has sender)
                if not tx.sender_address or tx.sender_address == self.monitored_wallet:
                    continue
                
                # Save to database (returns True if new)
                if self.db.save_transaction(tx.to_dict()):
                    new_transactions.append(tx)
            
            return new_transactions
            
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def get_recent_transactions(self, limit: int = 10) -> List[Transaction]:
        """Get recent transactions from database"""
        try:
            tx_data_list = self.db.get_recent_transactions(limit)
            return self._convert_to_transactions(tx_data_list)
        except Exception as e:
            print(f"Error getting recent transactions: {e}")
            return []
    
    def get_filtered_transactions(self, limit: int = 10, min_amount: float = None, 
                                max_amount: float = None, sender_address: str = None,
                                from_date: str = None, to_date: str = None) -> List[Transaction]:
        """Get filtered transactions from database"""
        try:
            tx_data_list = self.db.get_filtered_transactions(
                limit=limit,
                min_amount=min_amount,
                max_amount=max_amount,
                sender_address=sender_address,
                from_date=from_date,
                to_date=to_date
            )
            return self._convert_to_transactions(tx_data_list)
        except Exception as e:
            print(f"Error getting filtered transactions: {e}")
            return []
    
    def _convert_to_transactions(self, tx_data_list: List[dict]) -> List[Transaction]:
        """Convert database records to Transaction objects"""
        transactions = []
        for tx_data in tx_data_list:
            tx = Transaction(
                hash=tx_data['tx_hash'],
                account_id=tx_data['account_id'],
                sender_address=tx_data['sender_address'],
                sender_name=tx_data['sender_name'],
                amount_ton=tx_data['amount_ton'],
                amount_nanoton=tx_data['amount_nanoton'],
                message=tx_data['message'],
                timestamp=tx_data['timestamp'],
                block_number=tx_data['block_number'],
                confirmed=tx_data['confirmed'],
                processed=tx_data['processed']
            )
            transactions.append(tx)
        return transactions
    
    def get_transaction_stats(self) -> dict:
        """Get transaction statistics"""
        try:
            return self.db.get_stats()
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_transactions': 0,
                'total_amount': 0,
                'processed_count': 0,
                'confirmed_count': 0
            }
    
    def mark_transaction_processed(self, tx_hash: str) -> bool:
        """Mark transaction as processed"""
        try:
            self.db.mark_transaction_processed(tx_hash)
            return True
        except Exception as e:
            print(f"Error marking transaction processed: {e}")
            return False
    
    def get_account_info(self) -> Optional[dict]:
        """Get monitored account information"""
        try:
            return self.api_client.get_account_info(self.monitored_wallet)
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def get_wallet_balance(self) -> dict:
        """Get wallet balance information"""
        try:
            account_info = self.api_client.get_account_info(self.monitored_wallet)
            if account_info and 'balance' in account_info:
                balance_nanotons = int(account_info['balance'])
                balance_ton = balance_nanotons / 1_000_000_000  # Convert nanotons to TON
                return {
                    'balance_ton': balance_ton,
                    'balance_nanotons': balance_nanotons,
                    'status': account_info.get('state', 'unknown')
                }
            else:
                return {
                    'balance_ton': 0,
                    'balance_nanotons': 0,
                    'status': 'unknown'
                }
        except Exception as e:
            print(f"Error getting wallet balance: {e}")
            return {
                'balance_ton': 0,
                'balance_nanotons': 0,
                'status': 'error',
                'error': str(e)
            }
