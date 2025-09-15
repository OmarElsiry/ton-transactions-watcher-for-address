"""
Utility functions for TON Monitor
"""
import time
from datetime import datetime
from typing import Optional, Dict, Any

class FormatHelper:
    """Helper class for formatting data"""
    
    @staticmethod
    def format_ton_amount(amount: float) -> str:
        """Format TON amount with proper decimals"""
        return f"{amount:.2f}"
    
    @staticmethod
    def format_address(address: str, length: int = 20) -> str:
        """Format wallet address with truncation"""
        if not address:
            return "Unknown"
        return address[:length] + "..." if len(address) > length else address
    
    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """Format Unix timestamp to readable date"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_hash(tx_hash: str, length: int = 10) -> str:
        """Format transaction hash"""
        return tx_hash[:length] + "..." if len(tx_hash) > length else tx_hash

class ValidationHelper:
    """Helper class for data validation"""
    
    @staticmethod
    def is_valid_ton_address(address: str) -> bool:
        """Validate TON wallet address format"""
        if not address or len(address) < 40:
            return False
        return address.startswith(('UQ', 'EQ', 'kQ'))
    
    @staticmethod
    def is_valid_amount(amount: Any) -> bool:
        """Validate transaction amount"""
        try:
            float_amount = float(amount)
            return float_amount > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and validate filter parameters"""
        clean_filters = {}
        
        if filters.get('min_amount'):
            try:
                clean_filters['min_amount'] = float(filters['min_amount'])
            except (ValueError, TypeError):
                pass
        
        if filters.get('max_amount'):
            try:
                clean_filters['max_amount'] = float(filters['max_amount'])
            except (ValueError, TypeError):
                pass
        
        if filters.get('sender_address'):
            addr = str(filters['sender_address']).strip()
            if addr:
                clean_filters['sender_address'] = addr
        
        if filters.get('from_date'):
            clean_filters['from_date'] = str(filters['from_date'])
        
        if filters.get('to_date'):
            clean_filters['to_date'] = str(filters['to_date'])
        
        return clean_filters

class PerformanceHelper:
    """Helper class for performance optimization"""
    
    @staticmethod
    def cache_key(prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        return f"{prefix}:{'_'.join(str(arg) for arg in args)}"
    
    @staticmethod
    def rate_limit_check(last_call: Optional[float], min_interval: int) -> bool:
        """Check if enough time has passed since last call"""
        if last_call is None:
            return True
        return time.time() - last_call >= min_interval
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100):
        """Process items in batches for better performance"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

class ErrorHelper:
    """Helper class for error handling"""
    
    @staticmethod
    def safe_get(data: dict, key: str, default=None):
        """Safely get value from dictionary"""
        try:
            return data.get(key, default)
        except (AttributeError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Safely convert value to integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
