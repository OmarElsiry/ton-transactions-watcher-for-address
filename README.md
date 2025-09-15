# TON Wallet Monitor Service

A production-ready backend service to monitor TON wallet transactions with **manual control** and comprehensive API integration. This service uses free TON APIs with advanced native TON validation to ensure you only receive genuine TON coin transfers, not fake tokens.

## 🚀 Key Features

- 🎯 **Manual Control**: No automatic polling - full user control over sync timing
- 🛡️ **Native TON Validation**: Advanced multi-layer filtering blocks fake tokens and jettons
- 💾 **Transaction Storage**: SQLite database with complete transaction history
- 🌐 **Enhanced REST API**: Rich endpoints with full transaction data responses
- 🔧 **No API Keys Required**: Uses free TonCenter API with fallback support
- ⚙️ **Production Ready**: Clean architecture designed for scalable deployment
- 📊 **Real-time Data**: Manual sync returns complete transaction details
- 🔒 **Security First**: Multi-layer validation with opcode detection and pattern matching

## 🎯 Business Value

This service provides:
- **Manual Payment Processing**: On-demand detection of TON payments with full control
- **Complete Transaction Data**: Rich API responses with all transaction details
- **Advanced Security**: Multi-layer validation ensures only genuine TON coins are processed
- **Flexible Integration**: Manual sync API perfect for any application or website
- **Clean Architecture**: Modular design with reusable components for easy maintenance

## 🛡️ Advanced Native TON Validation

The service includes comprehensive multi-layer validation to ensure you only receive **genuine TON coins**:

- **Opcode Detection**: Identifies and blocks jetton transfer opcodes (0x0f8a7ea5, 0x178d4519, 0x7362d09c, 0x595f07bc)
- **Message Pattern Analysis**: Scans transaction messages for token transfer patterns
- **Value Verification**: Ensures transactions contain actual TON value, not zero-value token transfers
- **Conservative Filtering**: Fail-safe approach blocks suspicious transactions to prevent false positives
- **Multi-Layer Protection**: Validation occurs at both API client and transaction model levels

## 🚀 Quick Start (Local Development)

### 1. Installation

```bash
# Clone the project
cd monitor

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file - NO API KEYS REQUIRED!
vim .env
```

### 3. Run the Service

```bash
# Start the monitoring service
python app.py
```

The service will start in **manual-only mode** - no automatic polling occurs. Use the API endpoints to manually sync and retrieve transactions.
## 🌐 Production Deployment

### Remote Server Setup

Deploy the service on a remote server to monitor your TON wallet 24/7:

#### 1. Server Requirements

```bash
# Minimum server specs:
- 1 CPU core
- 512MB RAM
- 10GB storage
- Ubuntu 20.04+ or similar
- Python 3.8+
```

#### 2. Server Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Create application directory
sudo mkdir -p /opt/ton-monitor
sudo chown $USER:$USER /opt/ton-monitor
cd /opt/ton-monitor

# Clone your project
git clone <your-repo-url> .
# OR upload files via SCP/SFTP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Production Configuration

Create `/opt/ton-monitor/.env`:

```env
# TON Wallet to monitor
MONITORED_WALLET=UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315

# API Configuration (no keys required)
API_TYPE=toncenter
# POLLING_INTERVAL removed - manual sync only

# Server Configuration
FLASK_PORT=8080
FLASK_HOST=0.0.0.0
DATABASE_PATH=/opt/ton-monitor/data/transactions.db

# Transaction Filtering
MIN_AMOUNT_TON=0.01

# CORS Configuration (add your frontend domains)
CORS_ORIGINS=https://yourwebsite.com,https://app.yourwebsite.com
```

#### 4. Create System Service

Create `/etc/systemd/system/ton-monitor.service`:

```ini
[Unit]
Description=TON Wallet Monitor Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ton-monitor
Environment=PATH=/opt/ton-monitor/venv/bin
ExecStart=/opt/ton-monitor/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ton-monitor
sudo systemctl start ton-monitor

# Check status
sudo systemctl status ton-monitor
```

#### 5. Nginx Reverse Proxy (Optional)

Create `/etc/nginx/sites-available/ton-monitor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ton-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configuration Options

```env
# Core Settings
MONITORED_WALLET=your_ton_wallet_address
API_TYPE=toncenter                    # or 'tonapi'
# POLLING_INTERVAL removed - manual sync only
MIN_AMOUNT_TON=0.01                   # minimum TON amount to process

# Server Settings
FLASK_PORT=8080
FLASK_HOST=0.0.0.0                    # 0.0.0.0 for external access
DATABASE_PATH=./transactions.db

# Security Settings
CORS_ORIGINS=https://yoursite.com     # comma-separated allowed origins
```

## 🔌 API Integration

### REST API Endpoints

Use these endpoints to integrate with your applications:

#### Get Recent Transactions
```bash
GET http://your-server.com:8080/api/transactions?limit=10
```

Response:
```json
[
  {
    "tx_hash": "abc123...",
    "sender_address": "UQAbc123...",
    "amount_ton": 1.5,
    "amount_nanoton": 1500000000,
    "message": "Payment for services",
    "timestamp": 1640995200,
    "confirmed": true,
    "formatted_time": "2024-01-01 12:00:00"
  }
]
```

#### Get Wallet Balance
```bash
GET http://your-server.com:8080/api/balance
```

Response:
```json
{
  "balance_ton": 42.5,
  "balance_nanotons": 42500000000,
  "status": "active"
}
```

#### Get Statistics
```bash
GET http://your-server.com:8080/api/stats
```

Response:
```json
{
  "total_transactions": 150,
  "total_amount": 1250.75,
  "processed_count": 148,
  "confirmed_count": 150
}
```

#### Manual Sync (Enhanced)
```bash
POST http://your-server.com:8080/api/sync
Content-Type: application/json

{"limit": 10}
```

Response:
```json
{
  "status": "success",
  "new_transactions": 3,
  "message": "Found 3 new transactions",
  "transactions": [
    {
      "tx_hash": "HtD71OYE0F2JjKd2Flgv...",
      "amount_ton": 0.1,
      "sender_address": "EQAOvLwrhnaqkW_e1Qu8...",
      "formatted_time": "2025-09-15 01:00:14",
      "message": "te6cckEBAQEAAgAAAEysuc0="
    }
  ]
}
```

### Integration Examples

#### PHP Integration
```php
<?php
// Manual sync to get new transactions with full data
$syncData = json_encode(['limit' => 10]);
$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => $syncData
    ]
]);

$response = file_get_contents('http://your-server.com:8080/api/sync', false, $context);
$result = json_decode($response, true);

if ($result['status'] === 'success') {
    foreach ($result['transactions'] as $tx) {
        // Process each new transaction
        processPayment($tx['sender_address'], $tx['amount_ton'], $tx['tx_hash']);
    }
}

function processPayment($from, $amount, $txHash) {
    // Your payment processing logic
    echo "Received {$amount} TON from {$from} (Hash: {$txHash})";
}
?>
```

#### JavaScript/Node.js Integration
```javascript
const axios = require('axios');

class TONMonitorClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
    }
    
    async syncTransactions(limit = 10) {
        try {
            const response = await axios.post(`${this.serverUrl}/api/sync`, { limit });
            return response.data;
        } catch (error) {
            console.error('Error syncing transactions:', error);
            return { status: 'error', transactions: [] };
        }
    }
    
    async getBalance() {
        try {
            const response = await axios.get(`${this.serverUrl}/api/balance`);
            return response.data.balance_ton;
        } catch (error) {
            console.error('Error fetching balance:', error);
            return 0;
        }
    }
    
    async processNewPayments() {
        const result = await this.syncTransactions();
        
        if (result.status === 'success') {
            for (const tx of result.transactions) {
                console.log(`New payment: ${tx.amount_ton} TON from ${tx.sender_address}`);
                console.log(`Transaction hash: ${tx.tx_hash}`);
                console.log(`Time: ${tx.formatted_time}`);
                // Process payment logic here
            }
        }
    }
}

// Usage
const client = new TONMonitorClient('http://your-server.com:8080');
setInterval(() => client.processNewPayments(), 30000); // Check every 30 seconds
```

#### Python Integration
```python
import requests
import time

class TONMonitorClient:
    def __init__(self, server_url):
        self.server_url = server_url
    
    def sync_transactions(self, limit=10):
        try:
            response = requests.post(f"{self.server_url}/api/sync", 
                                   json={'limit': limit})
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return {'status': 'error', 'transactions': []}
    
    def get_balance(self):
        try:
            response = requests.get(f"{self.server_url}/api/balance")
            return response.json().get('balance_ton', 0)
        except Exception as e:
            print(f"Error: {e}")
            return 0
    
    def process_payments(self):
        result = self.sync_transactions()
        if result['status'] == 'success':
            for tx in result['transactions']:
                print(f"New payment: {tx['amount_ton']} TON from {tx['sender_address']}")
                print(f"Transaction hash: {tx['tx_hash']}")
                print(f"Time: {tx['formatted_time']}")
                # Your payment processing logic here
                self.credit_user_account(tx['sender_address'], tx['amount_ton'])

# Usage
client = TONMonitorClient('http://your-server.com:8080')
while True:
    client.process_payments()
    time.sleep(30)  # Check every 30 seconds
```

## 🔄 Multi-Server Architecture

### Backend Service + Frontend Application

Deploy the monitor service on one server and integrate with applications on other servers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Website  │    │  TON Monitor    │    │   TON Blockchain│
│  (Frontend)     │◄──►│   Service       │◄──►│                 │
│  any-domain.com │    │  monitor.com    │    │   Free APIs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Setup Example:

**Server 1: TON Monitor Service**
- Domain: `monitor.yourcompany.com`
- Runs: `app_simple.py`
- Purpose: Monitors blockchain, stores transactions

**Server 2: Your Main Application**
- Domain: `app.yourcompany.com`
- Integrates with: `http://monitor.yourcompany.com:8080/api/`
- Purpose: Your business logic, user interface

#### CORS Configuration

In your monitor service `.env`:
```env
CORS_ORIGINS=https://app.yourcompany.com,https://yourcompany.com,https://admin.yourcompany.com
```

### Load Balancing & High Availability

#### Multiple Monitor Instances
```bash
# Server 1: Primary monitor
MONITORED_WALLET=UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315
FLASK_PORT=8080

# Server 2: Backup monitor (same wallet)
MONITORED_WALLET=UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315
FLASK_PORT=8080
```

#### Nginx Load Balancer
```nginx
upstream ton_monitors {
    server monitor1.yourcompany.com:8080;
    server monitor2.yourcompany.com:8080 backup;
}

server {
    listen 80;
    server_name api.yourcompany.com;
    
    location /api/ {
        proxy_pass http://ton_monitors;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security & Best Practices

### Production Security

1. **Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

2. **SSL/HTTPS Setup**
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monitor.yourcompany.com
```

3. **Environment Security**
```bash
# Secure .env file
chmod 600 /opt/ton-monitor/.env
chown root:root /opt/ton-monitor/.env
```

4. **Database Security**
```bash
# Create secure database directory
sudo mkdir -p /opt/ton-monitor/data
sudo chown ubuntu:ubuntu /opt/ton-monitor/data
chmod 750 /opt/ton-monitor/data
```

### Monitoring & Logging

#### System Monitoring
```bash
# Check service status
sudo systemctl status ton-monitor

# View logs
sudo journalctl -u ton-monitor -f

# Check resource usage
top -p $(pgrep -f "python app.py")
```

#### Log Rotation
Create `/etc/logrotate.d/ton-monitor`:
```
/opt/ton-monitor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 ubuntu ubuntu
}
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Daily database backup
DATE=$(date +%Y%m%d)
cp /opt/ton-monitor/data/transactions.db /opt/ton-monitor/backups/transactions_$DATE.db
find /opt/ton-monitor/backups -name "*.db" -mtime +30 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /opt/ton-monitor/backup.sh
```

## Database Schema

The service uses SQLite with the following tables:

### Transactions Table
- `tx_hash` - Unique transaction hash
- `account_id` - Monitored wallet address
- `sender_address` - Transaction sender
- `amount_ton` - Amount in TON
- `amount_nanoton` - Amount in nanotons
- `message` - Transaction message/memo
- `timestamp` - Transaction timestamp
- `confirmed` - Confirmation status
- `processed` - Processing status

### Webhook Logs Table
- `webhook_id` - Webhook identifier
- `payload` - Raw webhook payload
- `processed` - Processing status
- `error_message` - Error details (if any)

## Security Features

### Webhook Signature Validation
```python
# Validates HMAC-SHA256 signature
def validate_webhook_signature(payload, signature):
    expected = hmac.new(secret_key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Transaction Filtering
- Minimum amount filtering to prevent spam
- Wallet address validation
- Duplicate transaction prevention
- Confirmation requirements

## Deployment

### Production Deployment

1. **Set up HTTPS**: Webhooks require HTTPS endpoints
2. **Configure Environment**: Set production environment variables
3. **Database**: Consider PostgreSQL for production
4. **Process Management**: Use systemd, supervisor, or Docker
5. **Monitoring**: Set up logging and health checks

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "app_api.py"]
```

### Systemd Service

```ini
[Unit]
Description=TON Wallet Monitor
After=network.target

[Service]
Type=simple
User=tonmonitor
WorkingDirectory=/opt/ton-monitor
ExecStart=/usr/bin/python3 app_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring and Logging

### Health Check Endpoint
```bash
curl http://localhost:8080/api/stats
```

### Log Files
- Application logs: Check console output
- Webhook logs: Stored in database
- Transaction logs: Stored in database

### Metrics
- Total transactions processed
- Total amount received
- Processing success rate
- Webhook delivery status

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Data**
   - Check TONAPI key configuration
   - Verify webhook endpoint is publicly accessible
   - Ensure HTTPS is configured properly
   - Check webhook registration status

2. **Database Errors**
   - Verify database file permissions
   - Check disk space
   - Ensure SQLite is properly installed

3. **Connection Issues**
   - Verify network connectivity
   - Check firewall settings
   - Ensure correct port configuration

### Debug Mode

```bash
# Run with debug logging
FLASK_DEBUG=1 python app.py
```

### Testing Webhooks

```bash
# Test webhook endpoint
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## API Reference

### Transaction Object

```json
{
  "tx_hash": "abc123...",
  "account_id": "UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315",
  "sender_address": "UQAbc123...",
  "amount_ton": 1.5,
  "amount_nanoton": 1500000000,
  "message": "Payment for services",
  "timestamp": 1640995200,
  "confirmed": true,
  "processed": false
}
```

### Webhook Payload

```json
{
  "type": "transaction",
  "hash": "abc123...",
  "from": "UQAbc123...",
  "amount": 1.5,
  "message": "Payment",
  "timestamp": 1640995200,
  "confirmed": true,
  "formatted_time": "2024-01-01 12:00:00"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Check TONAPI documentation at [docs.tonconsole.com](https://docs.tonconsole.com)

## Related Resources

- [TON Documentation](https://docs.ton.org)
- [TONAPI Documentation](https://docs.tonconsole.com)
- [TON Connect](https://docs.ton.org/develop/dapps/ton-connect)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io)
