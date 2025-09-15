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
    
    @staticmethod
    def render_dashboard():
        """Render the complete dashboard HTML"""
        from config import Config
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TON Wallet Monitor - API Backend</title>
            <style>
                {UIComponents.get_base_styles()}
                .api-endpoint {{
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .method {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .get {{ background: #d4edda; color: #155724; }}
                .post {{ background: #d1ecf1; color: #0c5460; }}
                .example-group {{
                    background: #f8f9fa;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #4facfe;
                }}
                    margin-top: 20px;
                    padding: 20px;
                }}
                .example-section {{
                    margin: 15px 0;
                }}
                .example-toggle {{
                    width: 100%;
                    text-align: left;
                    margin-bottom: 10px;
                }}
                .example-content {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #4facfe;
                }}
                .example-item {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }}
                .example-item h4 {{
                    margin: 0 0 10px 0;
                    color: #495057;
                }}
                .endpoint-url {{
                    background: #e9ecef;
                    padding: 8px;
                    border-radius: 4px;
                    font-family: monospace;
                    margin: 5px 0;
                    word-break: break-all;
                }}
                .time-builder, .amount-builder {{
                    background: #e8f4fd;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }}
                .time-builder input, .time-builder select, .amount-builder input {{
                    margin: 5px;
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                .test-results {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-top: 20px;
                    padding: 20px;
                }}
                #results-content {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    font-family: monospace;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {UIComponents.get_header_html(Config.MONITORED_WALLET)}
                {UIComponents.get_stats_html()}
                
                <div class="transactions">
                    <h2>API Endpoints & Examples</h2>
                    
                    <div class="api-endpoint">
                        <span class="method get">GET</span> <strong>/api/health</strong>
                        <p>Health check and system status</p>
                        <div class="endpoint-example">
                            <code>GET /api/health</code>
                            <button onclick="testAPI('/api/health', 'GET', 'health-result')" class="btn btn-success">Test</button>
                        </div>
                        <div id="health-result" class="test-result" style="display: none;"></div>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method get">GET</span> <strong>/api/balance</strong>
                        <p>Get current wallet balance</p>
                        <div class="endpoint-example">
                            <code>GET /api/balance</code>
                            <button onclick="testAPI('/api/balance', 'GET', 'balance-result')" class="btn btn-success">Test</button>
                        </div>
                        <div id="balance-result" class="test-result" style="display: none;"></div>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method post">POST</span> <strong>/api/sync</strong>
                        <p>Manually sync transactions from blockchain</p>
                        <div class="endpoint-example">
                            <code>POST /api/sync</code>
                            <button onclick="testAPI('/api/sync', 'POST', 'sync-result')" class="btn btn-success">Test</button>
                        </div>
                        <div id="sync-result" class="test-result" style="display: none;"></div>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method get">GET</span> <strong>/api/transactions</strong>
                        <p>Get transactions with filters:</p>
                        
                        <div class="example-group">
                            <h4>📊 Basic Limits</h4>
                            <div class="endpoint-examples">
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?limit=5</code>
                                    <button onclick="testAPI('/api/transactions?limit=5', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?limit=10</code>
                                    <button onclick="testAPI('/api/transactions?limit=10', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?limit=25</code>
                                    <button onclick="testAPI('/api/transactions?limit=25', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="example-group">
                            <h4>⏰ Time Filters</h4>
                            <div class="time-builder">
                                <input type="number" id="time-value" placeholder="Number" min="1" value="7" style="width: 60px;">
                                <select id="time-unit" style="width: 80px;">
                                    <option value="s">Sec</option>
                                    <option value="m">Min</option>
                                    <option value="h">Hour</option>
                                    <option value="d" selected>Day</option>
                                    <option value="w">Week</option>
                                    <option value="M">Month</option>
                                </select>
                                <button onclick="buildAndTestTime()" class="btn btn-primary">Test</button>
                            </div>
                            <div class="endpoint-examples">
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?minutes_ago=30</code>
                                    <button onclick="testAPI('/api/transactions?minutes_ago=30', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?hours_ago=24</code>
                                    <button onclick="testAPI('/api/transactions?hours_ago=24', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?days_ago=7</code>
                                    <button onclick="testAPI('/api/transactions?days_ago=7', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="example-group">
                            <h4>💰 Amount Filters</h4>
                            <div class="amount-builder">
                                <input type="number" id="min-amount" placeholder="Min" step="0.01" value="0.1" style="width: 60px;">
                                <input type="number" id="max-amount" placeholder="Max" step="0.01" value="10" style="width: 60px;">
                                <button onclick="buildAndTestAmount()" class="btn btn-primary">Test</button>
                            </div>
                            <div class="endpoint-examples">
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?min_amount=1.0</code>
                                    <button onclick="testAPI('/api/transactions?min_amount=1.0', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?min_amount=0.01&max_amount=0.1</code>
                                    <button onclick="testAPI('/api/transactions?min_amount=0.01&max_amount=0.1', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?min_amount=5.0</code>
                                    <button onclick="testAPI('/api/transactions?min_amount=5.0', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="example-group">
                            <h4>🔧 Combined Filters</h4>
                            <div class="endpoint-examples">
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?limit=20&min_amount=0.5&days_ago=3</code>
                                    <button onclick="testAPI('/api/transactions?limit=20&min_amount=0.5&days_ago=3', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                                <div class="endpoint-example">
                                    <code>GET /api/transactions?limit=10&hours_ago=12</code>
                                    <button onclick="testAPI('/api/transactions?limit=10&hours_ago=12', 'GET', 'tx-result')" class="btn btn-primary">Test</button>
                                </div>
                            </div>
                        </div>
                        
                        <div id="tx-result" class="test-result" style="display: none;"></div>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method get">GET</span> <strong>/api/stats</strong>
                        <p>Get transaction statistics</p>
                        <div class="endpoint-example">
                            <code>GET /api/stats</code>
                            <button onclick="testAPI('/api/stats', 'GET', 'stats-result')" class="btn btn-success">Test</button>
                        </div>
                        <div id="stats-result" class="test-result" style="display: none;"></div>
                    </div>
                </div>
                
                
            </div>
            
            <div id="notification" class="notification"></div>
            
            <script>
                {UIComponents.get_base_javascript()}
                
                // Load initial data
                document.addEventListener('DOMContentLoaded', function() {{
                    loadBalance();
                    loadStats();
                    
                    document.getElementById('refresh-btn').addEventListener('click', function() {{
                        loadBalance();
                        loadStats();
                        showNotification('🔄 Data refreshed');
                    }});
                    
                    document.getElementById('balance-btn').addEventListener('click', function() {{
                        loadBalance();
                        showNotification('💰 Balance updated');
                    }});
                }});
                
                async function loadBalance() {{
                    try {{
                        const response = await fetch('/api/balance');
                        const data = await response.json();
                        if (data.success && data.balance) {{
                            document.getElementById('wallet-balance').textContent = 
                                parseFloat(data.balance.balance_ton).toFixed(4);
                        }}
                    }} catch (error) {{
                        console.error('Error loading balance:', error);
                        document.getElementById('wallet-balance').textContent = 'Error';
                    }}
                }}
                
                async function loadStats() {{
                    try {{
                        const response = await fetch('/api/stats');
                        const data = await response.json();
                        if (data.success && data.stats) {{
                            document.getElementById('total-transactions').textContent = 
                                data.stats.total_transactions || 0;
                            document.getElementById('total-amount').textContent = 
                                parseFloat(data.stats.total_amount_ton || 0).toFixed(2);
                        }}
                    }} catch (error) {{
                        console.error('Error loading stats:', error);
                    }}
                }}
                
                function toggleExample(section) {{
                    const content = document.getElementById(section + '-examples');
                    if (content.style.display === 'none') {{
                        content.style.display = 'block';
                    }} else {{
                        content.style.display = 'none';
                    }}
                }}
                
                async function testAPI(endpoint, method = 'GET', resultId = 'test-results') {{
                    const resultDiv = document.getElementById(resultId);
                    
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<div style="color: #007bff; font-weight: bold;">🔄 Testing: ' + method + ' ' + endpoint + '</div><div style="margin-top: 10px; color: #6c757d;">Loading...</div>';
                    
                    try {{
                        const options = {{ method: method }};
                        if (method === 'POST') {{
                            options.headers = {{ 'Content-Type': 'application/json' }};
                            options.body = JSON.stringify({{ limit: 20 }});
                        }}
                        
                        const response = await fetch(endpoint, options);
                        const data = await response.json();
                        
                        const statusColor = response.status === 200 ? '#28a745' : '#dc3545';
                        const formattedJson = JSON.stringify(data, null, 2);
                        
                        resultDiv.innerHTML = 
                            '<div style="color: ' + statusColor + '; font-weight: bold; margin-bottom: 10px;">✅ Status: ' + response.status + '</div>' +
                            '<div style="background: #ffffff; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6; overflow-x: auto;"><pre style="margin: 0; color: #495057; font-size: 11px;">' + 
                            formattedJson + '</pre></div>';
                    }} catch (error) {{
                        resultDiv.innerHTML = '<div style="color: #dc3545; font-weight: bold;">❌ Error: ' + error.message + '</div>';
                    }}
                }}
                
                function buildAndTestTime() {{
                    const value = document.getElementById('time-value').value;
                    const unit = document.getElementById('time-unit').value;
                    
                    if (!value || value <= 0) {{
                        alert('Please enter a valid number');
                        return;
                    }}
                    
                    const unitMap = {{
                        's': 'seconds_ago',
                        'm': 'minutes_ago', 
                        'h': 'hours_ago',
                        'd': 'days_ago',
                        'w': 'weeks_ago',
                        'M': 'months_ago'
                    }};
                    
                    const param = unitMap[unit];
                    const url = '/api/transactions?' + param + '=' + value;
                    testAPI(url, 'GET', 'tx-result');
                }}
                
                function buildAndTestAmount() {{
                    const minAmount = document.getElementById('min-amount').value;
                    const maxAmount = document.getElementById('max-amount').value;
                    
                    if (!minAmount && !maxAmount) {{
                        alert('Please enter at least one amount value');
                        return;
                    }}
                    
                    const params = [];
                    if (minAmount) params.push('min_amount=' + minAmount);
                    if (maxAmount) params.push('max_amount=' + maxAmount);
                    
                    const url = '/api/transactions?' + params.join('&');
                    testAPI(url, 'GET', 'tx-result');
                }}
            </script>
        </body>
        </html>
        """
