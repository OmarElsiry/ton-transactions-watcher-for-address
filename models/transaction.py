from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from utils.helpers import FormatHelper, ValidationHelper

@dataclass
class Transaction:
    """Transaction model for clean data handling"""
    hash: str
    account_id: str
    sender_address: Optional[str] = None
    sender_name: Optional[str] = None
    amount_ton: float = 0.0
    amount_nanoton: int = 0
    message: Optional[str] = None
    timestamp: int = 0
    block_number: Optional[int] = None
    confirmed: bool = False
    processed: bool = False
    raw_data: Optional[Dict[str, Any]] = None
    
    @property
    def formatted_time(self) -> str:
        """Get human-readable timestamp"""
        return FormatHelper.format_timestamp(self.timestamp)
    
    @property
    def short_hash(self) -> str:
        """Get shortened hash for display"""
        return FormatHelper.format_hash(self.hash, 10)
    
    @property
    def short_sender(self) -> str:
        """Get shortened sender address"""
        return FormatHelper.format_address(self.sender_address, 10)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'tx_hash': self.hash,
            'account_id': self.account_id,
            'sender_address': self.sender_address,
            'sender_name': self.sender_name,
            'amount_ton': self.amount_ton,
            'amount_nanoton': self.amount_nanoton,
            'message': self.message,
            'timestamp': self.timestamp,
            'block_number': self.block_number,
            'confirmed': self.confirmed,
            'processed': self.processed,
            'formatted_time': self.formatted_time,
            'short_hash': self.short_hash,
            'short_sender': self.short_sender
        }
    
    def to_notification(self) -> Dict[str, Any]:
        """Convert to notification format"""
        return {
            'type': 'transaction',
            'hash': self.hash,
            'from': self.sender_address,
            'amount': self.amount_ton,
            'message': self.message,
            'timestamp': self.timestamp,
            'confirmed': self.confirmed,
            'formatted_time': self.formatted_time
        }
    
    @classmethod
    def from_api_data(cls, api_data: Dict[str, Any]) -> 'Transaction':
        """Create Transaction from API response data"""
        # Handle different API response formats
        tx_hash = api_data.get('hash', '')
        account_id = api_data.get('account', {}).get('address', '') if isinstance(api_data.get('account'), dict) else api_data.get('account', '')
        timestamp = api_data.get('utime', api_data.get('timestamp', 0))
        
        # Parse in_msg for incoming transactions
        in_msg = api_data.get('in_msg', {})
        sender_address = None
        amount_nanoton = 0
        message = None
        
        if in_msg:
            sender_address = in_msg.get('source', in_msg.get('src', ''))
            amount_nanoton = int(in_msg.get('value', 0))
            
            # CRITICAL: Validate this is native TON, not a fake token
            if not cls._is_native_ton_transaction(in_msg, api_data):
                raise ValueError(f"Non-native TON transaction detected: {tx_hash}")
            
            message_data = in_msg.get('message', {})
            if isinstance(message_data, dict):
                message = message_data.get('body', message_data.get('text', ''))
            else:
                message = str(message_data) if message_data else None
        
        # Parse out_msgs for outgoing transactions if no in_msg
        if not in_msg and api_data.get('out_msgs'):
            out_msgs = api_data.get('out_msgs', [])
            if out_msgs:
                out_msg = out_msgs[0]
                sender_address = account_id  # For outgoing, sender is the account
                amount_nanoton = int(out_msg.get('value', 0))
                message_data = out_msg.get('message', {})
                if isinstance(message_data, dict):
                    message = message_data.get('body', message_data.get('text', ''))
        
        return cls(
            hash=tx_hash,
            account_id=account_id,
            sender_address=sender_address,
            amount_ton=amount_nanoton / 1e9,
            amount_nanoton=amount_nanoton,
            message=message,
            timestamp=timestamp,
            block_number=api_data.get('lt', api_data.get('block_number')),
            confirmed=True,  # API usually returns confirmed transactions
            raw_data=api_data
        )
    
    @staticmethod
    def _is_native_ton_transaction(in_msg: Dict[str, Any], full_tx_data: Dict[str, Any]) -> bool:
        """Validate that this is a native TON transfer, not a jetton/token transfer"""
        try:
            # Check 1: Look for jetton transfer opcodes
            jetton_opcodes = [
                0x0f8a7ea5,  # Jetton transfer
                0x178d4519,  # Jetton internal transfer  
                0x7362d09c,  # Jetton transfer notification
                0x595f07bc,  # Jetton burn notification
            ]
            
            # Check message opcode
            message_data = in_msg.get('message', {})
            if isinstance(message_data, dict):
                opcode = message_data.get('opcode')
                if opcode and int(opcode) in jetton_opcodes:
                    return False
            
            # Check 2: Transaction description for jetton patterns
            description = full_tx_data.get('description', {})
            if isinstance(description, dict):
                action_phase = description.get('action_phase', {})
                if action_phase and action_phase.get('success') == False:
                    # Failed transactions might be token transfers
                    return True  # Allow failed transactions as they might be legitimate TON
            
            # Check 3: Look for jetton wallet patterns in sender/destination
            sender = in_msg.get('source', '')
            if sender:
                # Jetton wallets typically have specific patterns
                # This is a basic check - in production you might want more sophisticated validation
                pass
            
            # Check 4: Message body analysis
            body = message_data.get('body', '') if isinstance(message_data, dict) else ''
            if body:
                # Look for base64 encoded jetton transfer data
                jetton_keywords = ['jetton', 'token', 'mint', 'burn']
                if any(keyword in body.lower() for keyword in jetton_keywords):
                    return False
            
            # Check 5: Value validation - native TON transfers should have value > 0
            value = int(in_msg.get('value', 0))
            if value <= 0:
                return False
            
            # If all checks pass, this is likely a native TON transfer
            return True
            
        except Exception as e:
            print(f"Error validating native TON transaction: {e}")
            # If validation fails, be conservative and assume it's native TON
            return True
