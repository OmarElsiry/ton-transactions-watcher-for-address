from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import time

from config import Config
from services.transaction_service import TransactionService
from components.ui_components import UIComponents
from utils.helpers import ValidationHelper, FormatHelper

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize services
transaction_service = TransactionService(api_type=Config.API_TYPE)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/transactions')
def get_transactions():
    """Get recent transactions with filters"""
    limit = request.args.get('limit', 10, type=int)
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    sender_address = request.args.get('sender_address', type=str)
    from_date = request.args.get('from_date', type=str)
    to_date = request.args.get('to_date', type=str)
    
    transactions = transaction_service.get_filtered_transactions(
        limit=limit,
        min_amount=min_amount,
        max_amount=max_amount,
        sender_address=sender_address,
        from_date=from_date,
        to_date=to_date
    )
    return jsonify([tx.to_dict() for tx in transactions])

@app.route('/api/stats')
def get_stats():
    """Get transaction statistics"""
    stats = transaction_service.get_transaction_stats()
    return jsonify(stats)

@app.route('/api/balance')
def get_balance():
    """Get wallet balance"""
    try:
        account_info = transaction_service.get_account_info()
        if account_info:
            # Convert nanotons to TON
            balance_nanotons = int(account_info.get('balance', 0))
            balance_ton = balance_nanotons / 1e9
            return jsonify({
                'balance_ton': balance_ton,
                'balance_nanotons': balance_nanotons,
                'status': account_info.get('state', 'unknown')
            })
        return jsonify({'balance_ton': 0, 'balance_nanotons': 0, 'status': 'unknown'})
    except Exception as e:
        return jsonify({'error': str(e), 'balance_ton': 0}), 500

@app.route('/api/sync', methods=['POST'])
def sync_transactions():
    """Manually sync transactions from blockchain"""
    try:
        limit = request.json.get('limit', 10) if request.json else 10
        new_transactions = transaction_service.fetch_new_transactions(limit)
        
        return jsonify({
            'status': 'success',
            'new_transactions': len(new_transactions),
            'message': f'Found {len(new_transactions)} new transactions',
            'transactions': [tx.to_dict() for tx in new_transactions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Removed automatic periodic sync - now manual only

# Simple dashboard HTML template (no WebSocket)
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TON Wallet Monitor</title>
    <style>
        ''' + UIComponents.get_base_styles() + '''
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TON Wallet Monitor</h1>
            <div class="api-info">
                <strong>✅ Using Free API</strong> - No API keys required! 
                <br>API: ''' + Config.API_TYPE.title() + ''' (free) | Manual requests only
            </div>
            <p>Monitoring: <code>''' + Config.MONITORED_WALLET + '''</code></p>
            <div class="controls">
                <button id="refresh-btn" class="btn btn-primary">🔄 Refresh All</button>
                <button id="balance-btn" class="btn btn-success">💰 Update Balance</button>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card balance-card">
                <div class="stat-value" id="wallet-balance">0.00</div>
                <div class="stat-label">Wallet Balance (TON)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-transactions">0</div>
                <div class="stat-label">Total Transactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-amount">0.00</div>
                <div class="stat-label">Total Received (TON)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="api-type">''' + Config.API_TYPE.title() + '''</div>
                <div class="stat-label">API Provider</div>
            </div>
        </div>
        
        <div class="transactions">
            <div class="transaction-header">
                <h2>Recent Transactions</h2>
                <div class="filters">
                    <input type="number" id="min-amount" placeholder="Min TON" step="0.01" style="width: 80px;">
                    <input type="number" id="max-amount" placeholder="Max TON" step="0.01" style="width: 80px;">
                    <input type="text" id="sender-filter" placeholder="Sender address" style="width: 150px;">
                    <input type="date" id="from-date" style="width: 120px;">
                    <input type="date" id="to-date" style="width: 120px;">
                    <button id="apply-filters-btn" class="btn btn-primary">Apply Filters</button>
                    <button id="clear-filters-btn" class="btn btn-success">Clear</button>
                </div>
            </div>
            <div id="transaction-list">
                <div class="transaction-item">
                    <div>Loading transactions...</div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="notification" class="notification"></div>
    
    <script>
        let autoRefreshInterval;
        
        function loadBalance() {
            fetch('/api/balance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('wallet-balance').textContent = (data.balance_ton || 0).toFixed(2);
                })
                .catch(err => {
                    console.error('Error loading balance:', err);
                    document.getElementById('wallet-balance').textContent = 'Error';
                });
        }
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-transactions').textContent = data.total_transactions || 0;
                    document.getElementById('total-amount').textContent = (data.total_amount || 0).toFixed(2);
                })
                .catch(err => console.error('Error loading stats:', err));
        }
        
        function loadTransactions(filters = {}) {
            let url = '/api/transactions?limit=50';
            
            if (filters.min_amount) url += `&min_amount=${filters.min_amount}`;
            if (filters.max_amount) url += `&max_amount=${filters.max_amount}`;
            if (filters.sender_address) url += `&sender_address=${filters.sender_address}`;
            if (filters.from_date) url += `&from_date=${filters.from_date}`;
            if (filters.to_date) url += `&to_date=${filters.to_date}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    displayTransactions(data);
                })
                .catch(err => {
                    console.error('Error loading transactions:', err);
                    document.getElementById('transaction-list').innerHTML = 
                        '<div class="transaction-item"><div>Error loading transactions</div></div>';
                });
        }
        
        function displayTransactions(transactions) {
            const list = document.getElementById('transaction-list');
            if (transactions.length === 0) {
                list.innerHTML = '<div class="transaction-item"><div>No transactions yet - click "Manual Refresh" to fetch from blockchain</div></div>';
                return;
            }
            
            list.innerHTML = transactions.map(tx => `
                <div class="transaction-item">
                    <div>
                        <div class="transaction-amount">+${tx.amount_ton} TON</div>
                        <div class="transaction-from">From: ${tx.sender_address ? tx.sender_address.substring(0, 30) + '...' : 'Unknown'}</div>
                        <div class="transaction-time">${tx.formatted_time}</div>
                        ${tx.message ? '<div style="font-size: 12px; color: #888;">Message: ' + tx.message + '</div>' : ''}
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666;">${tx.tx_hash.substring(0, 10)}...</div>
                        <div style="font-size: 10px; color: #999;">${tx.confirmed ? '✅ Confirmed' : '⏳ Pending'}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        function refreshAll() {
            loadBalance();
            loadStats();
            loadTransactions();
        }
        
        // Event listeners
        document.getElementById('refresh-btn').addEventListener('click', function() {
            showNotification('🔄 Refreshing from blockchain...');
            fetch('/api/sync', {
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({limit: 10})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification(`✅ ${data.message}`);
                        refreshAll();
                    } else {
                        showNotification('❌ Refresh failed: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(err => {
                    showNotification('❌ Refresh failed: Network error');
                    console.error('Refresh error:', err);
                });
        });
        
        document.getElementById('balance-btn').addEventListener('click', function() {
            showNotification('💰 Updating balance...');
            loadBalance();
        });
        
        document.getElementById('apply-filters-btn').addEventListener('click', function() {
            const filters = {
                min_amount: document.getElementById('min-amount').value,
                max_amount: document.getElementById('max-amount').value,
                sender_address: document.getElementById('sender-filter').value,
                from_date: document.getElementById('from-date').value,
                to_date: document.getElementById('to-date').value
            };
            loadTransactions(filters);
            showNotification('🔍 Filters applied');
        });
        
        document.getElementById('clear-filters-btn').addEventListener('click', function() {
            document.getElementById('min-amount').value = '';
            document.getElementById('max-amount').value = '';
            document.getElementById('sender-filter').value = '';
            document.getElementById('from-date').value = '';
            document.getElementById('to-date').value = '';
            loadTransactions();
            showNotification('🗑️ Filters cleared');
        });
        
        // Initial load
        refreshAll();
        
        // No auto-refresh - manual only
        // autoRefreshInterval = setInterval(() => {
        //     refreshAll();
        // }, 30000);
        
        // Show initial status
        showNotification('🚀 TON Monitor loaded - No API keys needed!');
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Validate configuration
    Config.validate_config()
    
    # No automatic background sync - manual requests only
    
    print(f"🚀 Starting Manual TON Wallet Monitor")
    print(f"📡 API: {Config.API_TYPE.title()} (Free - No API key required)")
    print(f"👀 Monitoring: {Config.MONITORED_WALLET}")
    print(f"🔄 Manual requests only - No automatic polling")
    print(f"🌐 Dashboard: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"💡 Call /api/sync to fetch new transactions")
    
    # Run the Flask app
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=False
    )
