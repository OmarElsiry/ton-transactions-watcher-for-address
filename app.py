#!/usr/bin/env python3
"""
TON Wallet Monitor - API Backend for External Integration
Optimized Flask application with enhanced CORS support and API endpoints
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from datetime import datetime, timedelta

from config import Config
from services.transaction_service import TransactionService
from utils.helpers import ValidationHelper
from deposit_monitor import DepositMonitor
from realtime_deposit_notifier import realtime_notifier, DepositEvent
from database import TransactionDB

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
deposit_monitor = DepositMonitor(check_interval=30)
db = TransactionDB()

# Configure Flask templates
app.template_folder = 'templates'

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
        # Auto-sync: Fetch new transactions from blockchain first
        sync_limit = 50  # Fetch up to 50 new transactions
        new_transactions = transaction_service.fetch_new_transactions(sync_limit)
        
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 1000)  # Cap at 1000 for performance
        
        # Handle time-based filters
        filters = {
            'min_amount': request.args.get('min_amount', type=float),
            'max_amount': request.args.get('max_amount', type=float),
            'sender_address': request.args.get('sender_address'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date')
        }
        
        # Convert time-based parameters to from_date/to_date
        now = datetime.now()
        
        if request.args.get('minutes_ago'):
            minutes_ago = int(request.args.get('minutes_ago'))
            filters['from_date'] = (now - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
        elif request.args.get('hours_ago'):
            hours_ago = int(request.args.get('hours_ago'))
            filters['from_date'] = (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
        elif request.args.get('days_ago'):
            days_ago = int(request.args.get('days_ago'))
            filters['from_date'] = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
        elif request.args.get('weeks_ago'):
            weeks_ago = int(request.args.get('weeks_ago'))
            filters['from_date'] = (now - timedelta(weeks=weeks_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
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
            'new_transactions_found': len(new_transactions),
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

@app.route('/api/monitor/start', methods=['POST'])
def start_deposit_monitor():
    """Start the deposit monitor - External API"""
    try:
        if deposit_monitor.is_running:
            return jsonify({
                'success': False,
                'message': 'Monitor is already running',
                'status': deposit_monitor.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        deposit_monitor.start_monitoring()
        return jsonify({
            'success': True,
            'message': 'Deposit monitor started successfully',
            'status': deposit_monitor.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def stop_deposit_monitor():
    """Stop the deposit monitor - External API"""
    try:
        if not deposit_monitor.is_running:
            return jsonify({
                'success': False,
                'message': 'Monitor is not running',
                'status': deposit_monitor.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        deposit_monitor.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Deposit monitor stopped successfully',
            'status': deposit_monitor.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/monitor/status')
def get_monitor_status():
    """Get deposit monitor status - External API"""
    try:
        return jsonify({
            'success': True,
            'status': deposit_monitor.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/deposits/recent')
def get_recent_deposits():
    """Get recent deposits in JSON format - External API"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        # Get recent transactions (deposits only)
        transactions = transaction_service.get_recent_transactions(limit)
        
        # Format as deposit JSON objects
        deposits = []
        for tx in transactions:
            if tx.sender_address and tx.sender_address != Config.MONITORED_WALLET:
                deposit_data = {
                    "wallet_address": tx.sender_address,
                    "hash": tx.tx_hash,
                    "timestamp": tx.timestamp,
                    "amount": float(tx.amount_ton)
                }
                deposits.append(deposit_data)
        
        return jsonify({
            'success': True,
            'count': len(deposits),
            'deposits': deposits,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/deposits/realtime/start', methods=['POST'])
def start_realtime_deposits():
    """Start real-time deposit monitoring - External API"""
    try:
        if realtime_notifier.is_running:
            return jsonify({
                'success': False,
                'message': 'Real-time monitor is already running',
                'status': realtime_notifier.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        realtime_notifier.start_monitoring()
        return jsonify({
            'success': True,
            'message': 'Real-time deposit monitoring started',
            'status': realtime_notifier.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/deposits/realtime/stop', methods=['POST'])
def stop_realtime_deposits():
    """Stop real-time deposit monitoring - External API"""
    try:
        if not realtime_notifier.is_running:
            return jsonify({
                'success': False,
                'message': 'Real-time monitor is not running',
                'status': realtime_notifier.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        realtime_notifier.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Real-time deposit monitoring stopped',
            'status': realtime_notifier.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/deposits/realtime/next')
def get_next_deposit():
    """Get the next real-time deposit (blocking) - External API"""
    try:
        timeout = request.args.get('timeout', 30, type=int)  # Default 30 seconds timeout
        timeout = min(timeout, 300)  # Max 5 minutes
        
        if not realtime_notifier.is_running:
            return jsonify({
                'success': False,
                'error': 'Real-time monitor is not running. Start it first with POST /api/deposits/realtime/start',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Wait for next deposit
        deposit_event = realtime_notifier.get_next_deposit(timeout=timeout)
        
        if deposit_event:
            return jsonify({
                'success': True,
                'deposit': {
                    'wallet_address': deposit_event.wallet_address,
                    'hash': deposit_event.hash,
                    'timestamp': deposit_event.timestamp,
                    'amount': deposit_event.amount,
                    'detected_at': deposit_event.detected_at
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'deposit': None,
                'message': f'No deposits detected within {timeout} seconds',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/deposits/realtime/stream')
def stream_deposits():
    """Server-Sent Events stream for real-time deposits - External API"""
    def generate():
        yield "data: {\"status\": \"connected\", \"message\": \"Real-time deposit stream started\"}\n\n"
        
        if not realtime_notifier.is_running:
            yield "data: {\"error\": \"Real-time monitor is not running. Start it first.\"}\n\n"
            return
        
        while realtime_notifier.is_running:
            try:
                # Wait for next deposit with timeout
                deposit_event = realtime_notifier.get_next_deposit(timeout=10)
                
                if deposit_event:
                    deposit_data = {
                        'type': 'deposit',
                        'data': {
                            'wallet_address': deposit_event.wallet_address,
                            'hash': deposit_event.hash,
                            'timestamp': deposit_event.timestamp,
                            'amount': deposit_event.amount,
                            'detected_at': deposit_event.detected_at
                        }
                    }
                    yield f"data: {json.dumps(deposit_data)}\n\n"
                else:
                    # Send heartbeat
                    heartbeat = {
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
            except Exception as e:
                error_data = {
                    'type': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@app.route('/api/deposits/realtime/status')
def get_realtime_status():
    """Get real-time deposit monitor status - External API"""
    try:
        return jsonify({
            'success': True,
            'status': realtime_notifier.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/realtime/latest')
def get_latest_realtime_deposits():
    """Get latest real-time deposits from memory - For test website"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50
        
        latest_deposits = realtime_notifier.get_latest_deposits(limit)
        
        deposits = []
        for deposit in latest_deposits:
            deposits.append({
                'wallet_address': deposit.wallet_address,
                'hash': deposit.hash,
                'timestamp': deposit.timestamp,
                'amount': deposit.amount,
                'detected_at': deposit.detected_at
            })
        
        return jsonify({
            'success': True,
            'count': len(deposits),
            'deposits': deposits,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/realtime/start', methods=['POST'])
def start_realtime_monitoring():
    """Start real-time monitoring - For test website"""
    try:
        if realtime_notifier.is_running:
            return jsonify({
                'success': False,
                'message': 'Real-time monitor is already running',
                'status': realtime_notifier.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        realtime_notifier.start_monitoring()
        return jsonify({
            'success': True,
            'message': 'Real-time monitoring started',
            'status': realtime_notifier.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/realtime/stop', methods=['POST'])
def stop_realtime_monitoring():
    """Stop real-time monitoring - For test website"""
    try:
        if not realtime_notifier.is_running:
            return jsonify({
                'success': False,
                'message': 'Real-time monitor is not running',
                'status': realtime_notifier.get_status(),
                'timestamp': datetime.now().isoformat()
            })
        
        realtime_notifier.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Real-time monitoring stopped',
            'status': realtime_notifier.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status')
def get_api_status():
    """Get overall API status - For test website"""
    try:
        return jsonify({
            'success': True,
            'api_status': 'online',
            'monitored_wallet': Config.MONITORED_WALLET,
            'realtime_monitor': realtime_notifier.get_status(),
            'deposit_monitor': deposit_monitor.get_status(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/transactions/recent')
def get_recent_transactions_simple():
    """Get recent transactions in simple format - For test website"""
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        # Get transactions from database
        transactions = db.get_recent_transactions(limit)
        
        return jsonify({
            'success': True,
            'count': len(transactions),
            'transactions': transactions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/user-balance/<telegram_id>')
def get_user_balance_by_id(telegram_id):
    """Get user balance by telegram_id - For test website"""
    try:
        user_balance = db.get_user_balance(telegram_id)
        
        if user_balance:
            return jsonify({
                'success': True,
                'telegram_id': telegram_id,
                'wallet_address': user_balance.get('wallet_address'),
                'balance': user_balance.get('balance', 0.0),
                'created_at': user_balance.get('created_at'),
                'updated_at': user_balance.get('updated_at'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'telegram_id': telegram_id,
                'wallet_address': None,
                'balance': 0.0,
                'message': 'User not found, showing default balance',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/user-balances')
def get_all_user_balances():
    """Get all user balances - For test website"""
    try:
        user_balances = db.get_all_user_balances()
        
        return jsonify({
            'success': True,
            'count': len(user_balances),
            'user_balances': user_balances,
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
    """Main dashboard interface with real-time deposit monitoring"""
    return render_template('dashboard.html', MONITORED_WALLET=Config.MONITORED_WALLET)

@app.route('/example')
def example():
    """Serve the frontend example page"""
    try:
        with open('frontend_example.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Frontend example not found'}), 404

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
    print(f"   🔔 Real-time deposit endpoints:")
    print(f"   - POST /api/deposits/realtime/start")
    print(f"   - POST /api/deposits/realtime/stop")
    print(f"   - GET  /api/deposits/realtime/next")
    print(f"   - GET  /api/deposits/realtime/stream")
    print(f"   - GET  /api/deposits/realtime/status")
    
    # Run the Flask app
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=False
    )
