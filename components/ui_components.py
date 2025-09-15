"""
Shared UI components for TON Monitor dashboard
"""

class UIComponents:
    """Reusable UI components for the dashboard"""
    
    @staticmethod
    def get_base_styles():
        """Base CSS styles for all dashboards"""
        return """
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .api-info { background: #e8f5e8; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 24px; font-weight: bold; color: #2196F3; }
        .stat-label { color: #666; font-size: 14px; }
        .balance-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .balance-card .stat-value { color: white; }
        .balance-card .stat-label { color: #e0e0e0; }
        .transactions { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .transaction-header { padding: 20px; border-bottom: 1px solid #eee; }
        .filters { display: flex; gap: 10px; align-items: center; margin-top: 15px; flex-wrap: wrap; }
        .filters input { padding: 5px; border: 1px solid #ddd; border-radius: 4px; }
        .transaction-item { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .transaction-item:last-child { border-bottom: none; }
        .transaction-amount { font-weight: bold; color: #4CAF50; }
        .transaction-from { color: #666; font-size: 14px; }
        .transaction-time { color: #999; font-size: 12px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 0 5px; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .notification { position: fixed; top: 20px; right: 20px; padding: 15px; background: #4CAF50; color: white; border-radius: 4px; display: none; z-index: 1000; }
        .status-online { color: #4CAF50; font-weight: bold; }
        .status-offline { color: #f44336; font-weight: bold; }
        """
    
    @staticmethod
    def get_header_html(wallet_address, api_type="TonCenter"):
        """Generate header HTML"""
        return f"""
        <div class="header">
            <h1>TON Wallet Monitor</h1>
            <div class="api-info">
                <strong>✅ Using Free API</strong> - No API keys required! 
                <br>API: {api_type} (free) | Real-time monitoring
            </div>
            <p>Monitoring: <code>{wallet_address}</code></p>
            <div class="controls">
                <button id="refresh-btn" class="btn btn-primary">🔄 Refresh All</button>
                <button id="balance-btn" class="btn btn-success">💰 Update Balance</button>
            </div>
        </div>
        """
    
    @staticmethod
    def get_stats_html():
        """Generate stats section HTML"""
        return """
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
                <div class="stat-value" id="api-type">TonCenter</div>
                <div class="stat-label">API Provider</div>
            </div>
        </div>
        """
    
    @staticmethod
    def get_filters_html():
        """Generate filters HTML"""
        return """
        <div class="filters">
            <input type="number" id="min-amount" placeholder="Min TON" step="0.01" style="width: 80px;">
            <input type="number" id="max-amount" placeholder="Max TON" step="0.01" style="width: 80px;">
            <input type="text" id="sender-filter" placeholder="Sender address" style="width: 150px;">
            <input type="date" id="from-date" style="width: 120px;">
            <input type="date" id="to-date" style="width: 120px;">
            <button id="apply-filters-btn" class="btn btn-primary">Apply Filters</button>
            <button id="clear-filters-btn" class="btn btn-success">Clear</button>
        </div>
        """
    
    @staticmethod
    def get_transactions_html():
        """Generate transactions section HTML"""
        return f"""
        <div class="transactions">
            <div class="transaction-header">
                <h2>Recent Transactions</h2>
                {UIComponents.get_filters_html()}
            </div>
            <div id="transaction-list">
                <div class="transaction-item">
                    <div>Loading transactions...</div>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def get_base_javascript():
        """Base JavaScript functions for all dashboards"""
        return """
        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        }
        
        function formatTON(amount) {
            return parseFloat(amount).toFixed(2);
        }
        
        function formatAddress(address, length = 20) {
            if (!address) return 'Unknown';
            return address.length > length ? address.substring(0, length) + '...' : address;
        }
        
        function formatDate(timestamp) {
            return new Date(timestamp * 1000).toLocaleString();
        }
        
        function displayTransactions(transactions) {
            const list = document.getElementById('transaction-list');
            if (transactions.length === 0) {
                list.innerHTML = '<div class="transaction-item"><div>No transactions found</div></div>';
                return;
            }
            
            list.innerHTML = transactions.map(tx => `
                <div class="transaction-item">
                    <div>
                        <div class="transaction-amount">+${formatTON(tx.amount_ton)} TON</div>
                        <div class="transaction-from">From: ${formatAddress(tx.sender_address, 30)}</div>
                        <div class="transaction-time">${tx.formatted_time || formatDate(tx.timestamp)}</div>
                        ${tx.message ? '<div style="font-size: 12px; color: #888;">Message: ' + tx.message + '</div>' : ''}
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666;">${tx.tx_hash.substring(0, 10)}...</div>
                        <div style="font-size: 10px; color: #999;">${tx.confirmed ? '✅ Confirmed' : '⏳ Pending'}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function setupFilters() {
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
        }
        """
