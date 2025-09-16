import sqlite3
import json
from datetime import datetime
from config import Config

class TransactionDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE NOT NULL,
                    account_id TEXT NOT NULL,
                    sender_address TEXT,
                    sender_name TEXT,
                    amount_ton REAL NOT NULL,
                    amount_nanoton INTEGER NOT NULL,
                    message TEXT,
                    timestamp INTEGER NOT NULL,
                    block_number INTEGER,
                    confirmed BOOLEAN DEFAULT FALSE,
                    processed BOOLEAN DEFAULT FALSE,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS webhook_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_id TEXT,
                    payload TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_balances (
                    telegram_id TEXT PRIMARY KEY,
                    wallet_address TEXT,
                    balance REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tx_hash ON transactions(tx_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_account_id ON transactions(account_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions(timestamp)')
    
    def save_transaction(self, tx_data):
        """Save a transaction to the database"""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO transactions 
                    (tx_hash, account_id, sender_address, sender_name, amount_ton, 
                     amount_nanoton, message, timestamp, block_number, confirmed, 
                     processed, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx_data.get('tx_hash'),
                    tx_data.get('account_id'),
                    tx_data.get('sender_address'),
                    tx_data.get('sender_name'),
                    tx_data.get('amount_ton'),
                    tx_data.get('amount_nanoton'),
                    tx_data.get('message'),
                    tx_data.get('timestamp'),
                    tx_data.get('block_number'),
                    tx_data.get('confirmed', False),
                    tx_data.get('processed', False),
                    json.dumps(tx_data.get('raw_data', {}))
                ))
                return True
            except sqlite3.IntegrityError:
                # Transaction already exists
                return False
    
    def get_recent_transactions(self, limit=10):
        """Get recent transactions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM transactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_filtered_transactions(self, limit=10, min_amount=None, max_amount=None, 
                                sender_address=None, from_date=None, to_date=None):
        """Get filtered transactions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            
            if min_amount is not None:
                query += " AND amount_ton >= ?"
                params.append(min_amount)
            
            if max_amount is not None:
                query += " AND amount_ton <= ?"
                params.append(max_amount)
            
            if sender_address:
                query += " AND sender_address LIKE ?"
                params.append(f"%{sender_address}%")
            
            if from_date:
                try:
                    from datetime import datetime
                    # Try full datetime format first, then date-only format
                    try:
                        from_timestamp = int(datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S').timestamp())
                    except ValueError:
                        from_timestamp = int(datetime.strptime(from_date, '%Y-%m-%d').timestamp())
                    query += " AND timestamp >= ?"
                    params.append(from_timestamp)
                except ValueError:
                    pass
            
            if to_date:
                try:
                    from datetime import datetime
                    # Try full datetime format first, then date-only format
                    try:
                        to_timestamp = int(datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S').timestamp())
                    except ValueError:
                        to_timestamp = int(datetime.strptime(to_date, '%Y-%m-%d').timestamp()) + 86400  # End of day
                    query += " AND timestamp <= ?"
                    params.append(to_timestamp)
                except ValueError:
                    pass
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_transaction_by_hash(self, tx_hash):
        """Get a specific transaction by hash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM transactions WHERE tx_hash = ?
            ''', (tx_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def mark_transaction_processed(self, tx_hash):
        """Mark a transaction as processed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE transactions SET processed = TRUE WHERE tx_hash = ?
            ''', (tx_hash,))
    
    def log_webhook(self, webhook_id, payload, processed=False, error_message=None):
        """Log webhook activity"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO webhook_logs (webhook_id, payload, processed, error_message)
                VALUES (?, ?, ?, ?)
            ''', (webhook_id, json.dumps(payload), processed, error_message))
    
    def get_stats(self):
        """Get transaction statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_transactions,
                    COALESCE(SUM(amount_ton), 0) as total_amount,
                    COUNT(CASE WHEN processed = TRUE THEN 1 END) as processed_count,
                    COUNT(CASE WHEN confirmed = TRUE THEN 1 END) as confirmed_count
                FROM transactions
            ''')
            row = cursor.fetchone()
            return dict(row) if row else {
                'total_transactions': 0,
                'total_amount': 0,
                'processed_count': 0,
                'confirmed_count': 0
            }
    
    def get_user_balance(self, telegram_id):
        """Get user balance by telegram_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM user_balances WHERE telegram_id = ?
            ''', (telegram_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_or_update_user_balance(self, telegram_id, wallet_address=None, balance_change=0.0):
        """Create or update user balance"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if user exists
            cursor = conn.execute('SELECT balance FROM user_balances WHERE telegram_id = ?', (telegram_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing balance
                new_balance = existing[0] + balance_change
                conn.execute('''
                    UPDATE user_balances 
                    SET balance = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                ''', (new_balance, telegram_id))
            else:
                # Create new user with default telegram_id if none provided
                if not telegram_id or telegram_id == "0000000":
                    telegram_id = "0000000"  # Default telegram_id as requested
                
                conn.execute('''
                    INSERT INTO user_balances (telegram_id, wallet_address, balance)
                    VALUES (?, ?, ?)
                ''', (telegram_id, wallet_address, balance_change))
            
            return True
    
    def get_all_user_balances(self):
        """Get all user balances"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM user_balances ORDER BY updated_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
