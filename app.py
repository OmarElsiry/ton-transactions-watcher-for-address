#!/usr/bin/env python3
"""
TON Wallet Monitor - API Backend for External Integration
Optimized Flask application with enhanced CORS support and API endpoints
"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import time
import os
from datetime import datetime, timedelta

from config import Config
from services.transaction_service import TransactionService
from components.ui_components import UIComponents
from utils.helpers import ValidationHelper

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enhanced CORS configuration for external website integration
CORS(app, 
     origins=['*'],  # Allow all origins for external integration
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Initialize services
transaction_service = TransactionService(api_type=Config.API_TYPE)

# ============================================================================
# API ENDPOINTS FOR EXTERNAL INTEGRATION
# ============================================================================

@app.route('/api/health')
def health_check():
    """Health check endpoint for external monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_type': Config.API_TYPE,
        'monitored_wallet': Config.MONITORED_WALLET
    })

@app.route('/api/transactions')
def get_transactions():
    """Get transactions with optional filters - External API"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 1000)  # Cap at 1000 for performance
        
        filters = {
            'min_amount': request.args.get('min_amount', type=float),
            'max_amount': request.args.get('max_amount', type=float),
            'sender_address': request.args.get('sender_address'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date')
        }
        
        # Clean filters
        clean_filters = ValidationHelper.sanitize_filters(filters)
        
        # Get filtered transactions
        if clean_filters:
            transactions = transaction_service.get_filtered_transactions(
                limit=limit, **clean_filters
            )
        else:
            transactions = transaction_service.get_recent_transactions(limit)
        
        return jsonify({
            'success': True,
            'count': len(transactions),
            'transactions': [tx.to_dict() for tx in transactions],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/balance')
def get_balance():
    """Get wallet balance - External API"""
    try:
        balance = transaction_service.get_wallet_balance()
        return jsonify({
            'success': True,
            'balance': balance or {'balance_ton': 0.0},
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get transaction statistics - External API"""
    try:
        stats = transaction_service.get_transaction_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync', methods=['POST'])
def sync_transactions():
    """Manually sync transactions from blockchain - External API"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 10)
        limit = min(limit, 100)  # Cap at 100 for performance
        
        new_transactions = transaction_service.fetch_new_transactions(limit)
        
        return jsonify({
            'success': True,
            'status': 'completed',
            'new_transactions': len(new_transactions),
            'message': f'Found {len(new_transactions)} new transactions',
            'transactions': [tx.to_dict() for tx in new_transactions],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/verify/transaction/<tx_hash>')
def verify_transaction(tx_hash):
    """Verify a specific transaction by hash - For external verification"""
    try:
        # Get transaction from database
        transactions = transaction_service.get_recent_transactions(1000)
        transaction = next((tx for tx in transactions if tx.tx_hash == tx_hash), None)
        
        if transaction:
            return jsonify({
                'success': True,
                'verified': True,
                'transaction': transaction.to_dict(),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'verified': False,
                'message': 'Transaction not found in monitored wallet',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/verify/payment')
def verify_payment():
    """Verify payment by amount and timeframe - For external payment verification"""
    try:
        # Get parameters
        amount = request.args.get('amount', type=float)
        sender = request.args.get('sender')
        minutes_ago = request.args.get('minutes_ago', 60, type=int)
        
        if not amount:
            return jsonify({
                'success': False,
                'error': 'Amount parameter is required'
            }), 400
        
        # Calculate time range
        now = datetime.now()
        from_time = now - timedelta(minutes=minutes_ago)
        
        # Get recent transactions
        transactions = transaction_service.get_filtered_transactions(
            limit=1000,
            min_amount=amount * 0.99,  # Allow 1% tolerance
            max_amount=amount * 1.01,
            from_date=from_time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Filter by sender if provided
        if sender:
            transactions = [tx for tx in transactions if tx.sender_address == sender]
        
        verified_payments = []
        for tx in transactions:
            if abs(float(tx.amount_ton) - amount) <= (amount * 0.01):  # 1% tolerance
                verified_payments.append(tx.to_dict())
        
        return jsonify({
            'success': True,
            'verified': len(verified_payments) > 0,
            'payment_count': len(verified_payments),
            'payments': verified_payments,
            'search_criteria': {
                'amount': amount,
                'sender': sender,
                'minutes_ago': minutes_ago
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/wallet/info')
def get_wallet_info():
    """Get wallet information - External API"""
    try:
        account_info = transaction_service.get_account_info()
        balance = transaction_service.get_wallet_balance()
        stats = transaction_service.get_transaction_stats()
        
        return jsonify({
            'success': True,
            'wallet_address': Config.MONITORED_WALLET,
            'account_info': account_info,
            'balance': balance,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# WEB DASHBOARD (Optional - for internal monitoring)
# ============================================================================

@app.route('/')
def dashboard():
    """Main dashboard interface"""
    return UIComponents.render_dashboard()

@app.route('/example')
def example():
    """Serve the frontend example page"""
    with open('frontend_example.html', 'r', encoding='utf-8') as f:
        return f.read()


# Dashboard HTML template (simplified)
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TON Wallet Monitor - API Backend</title>
    <style>
        ''' + UIComponents.get_base_styles() + '''
        .api-endpoint {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }
        .get { background: #d4edda; color: #155724; }
        .post { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TON Wallet Monitor - API Backend</h1>
            <div class="api-info">
                <strong>✅ External API Ready</strong> - CORS enabled for cross-origin requests
                <br>Monitoring: <code>''' + Config.MONITORED_WALLET + '''</code>
            </div>
            <div class="controls">
                <button id="test-api-btn" class="btn btn-primary">🧪 Test API</button>
                <button id="sync-btn" class="btn btn-success">🔄 Sync Now</button>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="wallet-balance">0.00</div>
                <div class="stat-label">Balance (TON)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-transactions">0</div>
                <div class="stat-label">Total Transactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="api-status">Ready</div>
                <div class="stat-label">API Status</div>
            </div>
        </div>
        
        <div class="transactions">
            <h2>Available API Endpoints</h2>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/health</strong>
                <p>Health check and system status</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/transactions</strong>
                <p>Get transactions with optional filters (limit, min_amount, max_amount, sender_address, from_date, to_date)</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/balance</strong>
                <p>Get current wallet balance</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/stats</strong>
                <p>Get transaction statistics</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method post">POST</span> <strong>/api/sync</strong>
                <p>Manually sync transactions from blockchain</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/verify/transaction/&lt;tx_hash&gt;</strong>
                <p>Verify a specific transaction by hash</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/verify/payment</strong>
                <p>Verify payment by amount and timeframe (amount, sender, minutes_ago)</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method get">GET</span> <strong>/api/wallet/info</strong>
                <p>Get complete wallet information</p>
            </div>
        </div>
    </div>
    
    <div id="notification" class="notification"></div>
    
    <script>
        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('total-transactions').textContent = data.stats.total_transactions || 0;
                        document.getElementById('api-status').textContent = 'Active';
                    }
                })
                .catch(err => {
                    document.getElementById('api-status').textContent = 'Error';
                    console.error('Error loading stats:', err);
                });
        }
        
        function loadBalance() {
            fetch('/api/balance')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('wallet-balance').textContent = 
                            (data.balance.balance_ton || 0).toFixed(2);
                    }
                })
                .catch(err => {
                    document.getElementById('wallet-balance').textContent = 'Error';
                    console.error('Error loading balance:', err);
                });
        }
        
        document.getElementById('test-api-btn').addEventListener('click', function() {
            showNotification('🧪 Testing API endpoints...');
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'healthy') {
                        showNotification('✅ API is working correctly');
                        loadStats();
                        loadBalance();
                    } else {
                        showNotification('❌ API health check failed');
                    }
                })
                .catch(err => {
                    showNotification('❌ API test failed');
                    console.error('API test error:', err);
                });
        });
        
        document.getElementById('sync-btn').addEventListener('click', function() {
            showNotification('🔄 Syncing transactions...');
            fetch('/api/sync', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({limit: 10})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(`✅ ${data.message}`);
                        loadStats();
                    } else {
                        showNotification('❌ Sync failed: ' + data.error);
                    }
                })
                .catch(err => {
                    showNotification('❌ Sync failed: Network error');
                    console.error('Sync error:', err);
                });
        });
        
        // Initial load
        loadStats();
        loadBalance();
        showNotification('🚀 TON Monitor API Backend Ready');
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Validate configuration
    Config.validate_config()
    
    print(f"🚀 Starting TON Wallet Monitor API Backend")
    print(f"📡 API: {Config.API_TYPE.title()} (Free - No API key required)")
    print(f"👀 Monitoring: {Config.MONITORED_WALLET}")
    print(f"🌐 Dashboard: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"🔗 External API: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/api/")
    print(f"✅ CORS enabled for external integration")
    print(f"💡 Available endpoints:")
    print(f"   - GET  /api/health")
    print(f"   - GET  /api/transactions")
    print(f"   - GET  /api/balance")
    print(f"   - GET  /api/stats")
    print(f"   - POST /api/sync")
    print(f"   - GET  /api/verify/transaction/<hash>")
    print(f"   - GET  /api/verify/payment")
    print(f"   - GET  /api/wallet/info")
    
    # Run the Flask app
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=False
    )
