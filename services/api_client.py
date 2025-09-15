import requests
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from models.transaction import Transaction

class APIClient(ABC):
    """Abstract base class for TON API clients"""
    
    @abstractmethod
    def get_transactions(self, account_id: str, limit: int = 10) -> List[Transaction]:
        """Get transactions for account"""
        pass
    
    @abstractmethod
    def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account information"""
        pass

class TonCenterAPI(APIClient):
    """Free TON Center API client - no API key required"""
    
    def __init__(self):
        self.base_url = "https://toncenter.com/api/v2"
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def get_transactions(self, account_id: str, limit: int = 10) -> List[Transaction]:
        """Get transactions using free TonCenter API"""
        url = f"{self.base_url}/getTransactions"
        params = {
            'address': account_id,
            'limit': limit,
            'to_lt': 0,
            'archival': True
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('ok'):
                print(f"API Error: {data.get('error', 'Unknown error')}")
                return []
            
            transactions = []
            for tx_data in data.get('result', []):
                try:
                    # Convert TonCenter format to our Transaction model
                    tx = self._parse_toncenter_transaction(tx_data, account_id)
                    if tx:
                        transactions.append(tx)
                except Exception as e:
                    print(f"Error parsing transaction: {e}")
                    continue
            
            return transactions
            
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account info using free TonCenter API"""
        url = f"{self.base_url}/getAddressInformation"
        params = {'address': account_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('ok'):
                return data.get('result', {})
            return None
            
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def _parse_toncenter_transaction(self, tx_data: Dict[str, Any], account_id: str) -> Optional[Transaction]:
        """Parse TonCenter transaction format"""
        try:
            # Extract basic transaction info
            tx_hash = tx_data.get('transaction_id', {}).get('hash', '')
            timestamp = int(tx_data.get('utime', 0))
            
            # Parse in_msg for incoming transactions
            in_msg = tx_data.get('in_msg', {})
            sender_address = None
            amount_nanoton = 0
            message = None
            
            if in_msg and in_msg.get('source'):
                sender_address = in_msg.get('source', '')
                amount_nanoton = int(in_msg.get('value', 0))
                
                # CRITICAL: Validate this is native TON, not a token transfer
                if not self._is_native_ton_transfer(in_msg):
                    print(f"Skipping non-native TON transfer: {tx_hash}")
                    return None
                
                # Try to extract message
                msg_data = in_msg.get('msg_data', {})
                if msg_data:
                    message = msg_data.get('text', msg_data.get('body', ''))
            
            # Skip if no meaningful transaction data
            if not sender_address and amount_nanoton == 0:
                return None
            
            return Transaction(
                hash=tx_hash,
                account_id=account_id,
                sender_address=sender_address,
                amount_ton=amount_nanoton / 1e9,
                amount_nanoton=amount_nanoton,
                message=message,
                timestamp=timestamp,
                block_number=tx_data.get('transaction_id', {}).get('lt'),
                confirmed=True,
                raw_data=tx_data
            )
            
        except Exception as e:
            print(f"Error parsing transaction: {e}")
            return None
    
    def _is_native_ton_transfer(self, in_msg: Dict[str, Any]) -> bool:
        """Validate that this is a native TON transfer, not a token transfer"""
        try:
            # Native TON transfers have specific characteristics:
            # 1. No op_code for token transfers (like 0x0f8a7ea5 for jettons)
            # 2. Direct value transfer without token contract interaction
            # 3. No jetton/token-specific message structure
            
            msg_data = in_msg.get('msg_data', {})
            
            # Check for jetton transfer op codes
            jetton_transfer_opcodes = [
                '0x0f8a7ea5',  # Jetton transfer
                '0x178d4519',  # Jetton internal transfer
                '0x7362d09c',  # Jetton transfer notification
            ]
            
            # Check if message contains jetton transfer opcode
            if isinstance(msg_data, dict):
                op_code = msg_data.get('op_code')
                if op_code and str(op_code).lower() in [code.lower() for code in jetton_transfer_opcodes]:
                    return False
            
            # Check message body for jetton patterns
            body = msg_data.get('body', '') if isinstance(msg_data, dict) else str(msg_data)
            if body:
                # Common jetton transfer patterns
                jetton_patterns = ['jetton', 'token', 'transfer_notification']
                if any(pattern in body.lower() for pattern in jetton_patterns):
                    return False
            
            # Check for direct value transfer (native TON characteristic)
            value = int(in_msg.get('value', 0))
            if value > 0:
                # This is likely a native TON transfer
                return True
            
            return False
            
        except Exception as e:
            print(f"Error validating TON transfer: {e}")
            # If validation fails, assume it's native TON to be safe
            return True

class TonAPIFree(APIClient):
    """Free TonAPI client - alternative free API"""
    
    def __init__(self):
        self.base_url = "https://tonapi.io/v2"
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def get_transactions(self, account_id: str, limit: int = 10) -> List[Transaction]:
        """Get transactions using free TonAPI"""
        url = f"{self.base_url}/accounts/{account_id}/transactions"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for tx_data in data.get('transactions', []):
                try:
                    tx = Transaction.from_api_data(tx_data)
                    transactions.append(tx)
                except Exception as e:
                    print(f"Error parsing transaction: {e}")
                    continue
            
            return transactions
            
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account info using free TonAPI"""
        url = f"{self.base_url}/accounts/{account_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None

class APIClientFactory:
    """Factory to create API clients - easy to switch APIs"""
    
    @staticmethod
    def create_client(api_type: str = "toncenter") -> APIClient:
        """Create API client based on type"""
        if api_type.lower() == "toncenter":
            return TonCenterAPI()
        elif api_type.lower() == "tonapi":
            return TonAPIFree()
        else:
            # Default to TonCenter (most reliable free API)
            return TonCenterAPI()
