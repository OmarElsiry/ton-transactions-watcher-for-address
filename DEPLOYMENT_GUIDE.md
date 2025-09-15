# TON Wallet Monitor - Manual Control Deployment Guide

A production-ready backend service to monitor TON wallet transactions with **manual control** and comprehensive API integration. **No API keys required** - uses free blockchain APIs.

## 🚀 What This Service Does

- **Manual TON wallet monitoring** - full user control over sync timing
- **Enhanced REST API** with complete transaction data responses
- **Advanced security filtering** - blocks fake tokens and jettons with multi-layer validation
- **Rich transaction storage** with comprehensive filtering by amount, date, sender address
- **Remote deployment ready** - deploy on any server and access from anywhere

## 📋 Quick Installation

### 1. Install Dependencies

```bash
# Install Python (if not installed)
# Windows: Download from python.org
# Linux: sudo apt install python3 python3-pip

# Install required packages
pip install flask flask-cors requests python-dotenv
```

### 2. Download and Setup

```bash
# Create project directory
mkdir ton-monitor
cd ton-monitor

# Copy all project files to this directory
# (app.py, config.py, database.py, services/, models/, components/, utils/, .env)

# Edit configuration
cp .env.example .env
vim .env  # Edit your wallet address
```

### 3. Configure Your Wallet

Edit `.env` file:
```env
MONITORED_WALLET=UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315
API_TYPE=toncenter
# POLLING_INTERVAL removed - manual sync only
MIN_AMOUNT_TON=0.01
FLASK_PORT=8080
FLASK_HOST=0.0.0.0
```

### 4. Run the Service

```bash
# Start the manual monitoring service
python app.py

# Service will start on http://localhost:8080
# Dashboard: http://localhost:8080
# API: http://localhost:8080/api/transactions
# Manual Sync: POST http://localhost:8080/api/sync
```

## 🌐 Remote Server Deployment

### Deploy on VPS/Cloud Server

**Step 1: Get a Server**
- Any VPS (DigitalOcean, Linode, AWS, etc.)
- Minimum: 1 CPU, 512MB RAM, Ubuntu 20.04+

**Step 2: Server Setup**
```bash
# Connect to your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv -y

# Create app directory
mkdir -p /opt/ton-monitor
cd /opt/ton-monitor

# Upload your files (use SCP, SFTP, or git)
# Example with SCP:
# scp -r /local/ton-monitor/* root@your-server-ip:/opt/ton-monitor/

# Install dependencies
pip3 install flask flask-cors requests python-dotenv
```

**Step 3: Configure for Remote Access**
```bash
# Edit .env file
nano .env
```

Set these values:
```env
MONITORED_WALLET=your_ton_wallet_address_here
FLASK_HOST=0.0.0.0  # Important: allows external connections
FLASK_PORT=8080
CORS_ORIGINS=https://yourwebsite.com,https://app.yourwebsite.com
```

**Step 4: Run as Background Service**
```bash
# Create service file
nano /etc/systemd/system/ton-monitor.service
```

Add this content:
```ini
[Unit]
Description=TON Wallet Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ton-monitor
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
systemctl daemon-reload
systemctl enable ton-monitor
systemctl start ton-monitor

# Check status
systemctl status ton-monitor
```

## 🔗 Understanding URLs: Localhost vs Remote

### What is Localhost?

- **localhost** = your own computer
- **127.0.0.1** = same as localhost
- Only works when accessing from the same computer

### Remote Server URLs

When you deploy on a remote server, replace localhost with your server's address:

**Examples:**

| Deployment | Dashboard URL | API URL |
|------------|---------------|---------|
| Local computer | `http://localhost:8080` | `http://localhost:8080/api/transactions` |
| Server IP: 192.168.1.100 | `http://192.168.1.100:8080` | `http://192.168.1.100:8080/api/transactions` |
| Domain: monitor.mysite.com | `http://monitor.mysite.com:8080` | `http://monitor.mysite.com:8080/api/transactions` |

### Getting Your Server IP/Domain

```bash
# Find your server's public IP
curl ifconfig.me

# Example result: 203.0.113.45
# Your API URL becomes like: http://203.0.113.45:8080/api/transactions
```

## 🔌 Using the API from Your Website

### Basic API Usage

**Get Recent Transactions:**
```bash
GET http://your-server-ip:8080/api/transactions
```

**Get Filtered Transactions:**
```bash
# Transactions over 0.5 TON
GET http://your-server-ip:8080/api/transactions?min_amount=0.5

# From specific sender
GET http://your-server-ip:8080/api/transactions?sender_address=UQAbc123

# Date range
GET http://your-server-ip:8080/api/transactions?from_date=2024-01-01&to_date=2024-01-31

# Combined filters
GET http://your-server-ip:8080/api/transactions?min_amount=1.0&max_amount=10.0&from_date=2024-01-01
```

**Get Wallet Balance:**
```bash
GET http://your-server-ip:8080/api/balance
```

### Integration Examples

**PHP Example (Manual Sync):**
```php
<?php
$server_url = "http://203.0.113.45:8080";  // Your server IP

// Manual sync to get new transactions
$syncData = json_encode(['limit' => 10]);
$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => $syncData
    ]
]);

$response = file_get_contents("$server_url/api/sync", false, $context);
$result = json_decode($response, true);

if ($result['status'] === 'success') {
    foreach ($result['transactions'] as $tx) {
        echo "New payment: {$tx['amount_ton']} TON from {$tx['sender_address']}\n";
        processPayment($tx['sender_address'], $tx['amount_ton'], $tx['tx_hash']);
    }
}

function processPayment($from, $amount, $txHash) {
    // Your payment processing logic
    // Update user balance, send confirmation email, etc.
}
?>
```

**JavaScript Example (Manual Sync):**
```javascript
const SERVER_URL = "http://203.0.113.45:8080";  // Your server IP

async function syncAndProcessPayments() {
    try {
        // Manual sync to get new transactions
        const response = await fetch(`${SERVER_URL}/api/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limit: 10 })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            result.transactions.forEach(tx => {
                console.log(`New payment: ${tx.amount_ton} TON from ${tx.sender_address}`);
                console.log(`Transaction hash: ${tx.tx_hash}`);
                processPayment(tx);
            });
        }
    } catch (error) {
        console.error('Error syncing payments:', error);
    }
}

function processPayment(transaction) {
    // Your payment processing logic
    // Update UI, credit user account, etc.
}

// Manual sync every 30 seconds
setInterval(syncAndProcessPayments, 30000);
```

**Python Example (Manual Sync):**
```python
import requests
import time

SERVER_URL = "http://203.0.113.45:8080"  # Your server IP

def sync_and_process_payments():
    try:
        # Manual sync to get new transactions
        response = requests.post(f"{SERVER_URL}/api/sync", 
                               json={'limit': 10})
        result = response.json()
        
        if result['status'] == 'success':
            for tx in result['transactions']:
                print(f"New payment: {tx['amount_ton']} TON from {tx['sender_address']}")
                print(f"Transaction hash: {tx['tx_hash']}")
                print(f"Time: {tx['formatted_time']}")
                process_payment(tx)
            
    except Exception as e:
        print(f"Error: {e}")

def process_payment(transaction):
    # Your payment processing logic
    pass

# Manual sync every 30 seconds
while True:
    sync_and_process_payments()
    time.sleep(30)
```

## 🔍 Frontend Filters

The dashboard includes built-in filters:

- **Amount Range**: Filter by minimum/maximum TON amount
- **Sender Address**: Search for specific wallet addresses
- **Date Range**: Filter transactions by date
- **Combined Filters**: Use multiple filters together

**Filter Examples:**
- Show only payments > 1 TON: Set "Min TON" to 1.0
- Find payments from specific user: Enter their wallet address
- View last week's transactions: Set date range

## 🛡️ Security Features

### Native TON Validation

The service automatically filters out fake tokens:

- **Jetton Detection**: Identifies and blocks token transfers
- **Opcode Analysis**: Checks transaction opcodes for token patterns
- **Message Validation**: Scans transaction messages for fake token signatures
- **Value Verification**: Ensures transactions have real TON value

### Security Best Practices

**Server Security:**
```bash
# Basic firewall
ufw allow 22    # SSH
ufw allow 8080  # Your service
ufw enable

# Secure file permissions
chmod 600 .env
chmod 755 app_simple.py
```

**API Security:**
- Configure CORS origins in `.env`
- Use HTTPS in production (with nginx/apache)
- Monitor logs for unusual activity

## 🔧 Configuration Options

### Environment Variables (.env)

```env
# Required Settings
MONITORED_WALLET=UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315

# API Settings (no keys required)
API_TYPE=toncenter          # Free API provider
POLLING_INTERVAL=10         # Check blockchain every 10 seconds

# Server Settings
FLASK_PORT=8080            # Service port
FLASK_HOST=0.0.0.0         # 0.0.0.0 = allow external connections
DATABASE_PATH=./transactions.db

# Filtering
MIN_AMOUNT_TON=0.01        # Minimum transaction amount to process

# Security
CORS_ORIGINS=https://yourwebsite.com,https://app.yourwebsite.com
```

### API Parameters

**Transaction Filters:**
- `limit`: Number of transactions to return (default: 10, max: 100)
- `min_amount`: Minimum TON amount
- `max_amount`: Maximum TON amount  
- `sender_address`: Filter by sender (partial match)
- `from_date`: Start date (YYYY-MM-DD format)
- `to_date`: End date (YYYY-MM-DD format)

**Example API Calls:**
```bash
# Last 50 transactions
GET /api/transactions?limit=50

# Big payments only
GET /api/transactions?min_amount=10.0

# Specific sender
GET /api/transactions?sender_address=UQAbc123

# Date range
GET /api/transactions?from_date=2024-01-01&to_date=2024-01-31

# Combined filters
GET /api/transactions?min_amount=1.0&sender_address=UQAbc&from_date=2024-01-01
```

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
journalctl -u ton-monitor -f

# Check if port is in use
netstat -tulpn | grep 8080

# Restart service
systemctl restart ton-monitor
```

**Can't access from external website:**
```bash
# Check firewall
ufw status

# Verify FLASK_HOST=0.0.0.0 in .env
cat .env | grep FLASK_HOST

# Check CORS settings
cat .env | grep CORS_ORIGINS
```

**No transactions showing:**
```bash
# Check if wallet address is correct
cat .env | grep MONITORED_WALLET

# Test API manually
curl http://localhost:8080/api/transactions

# Check service logs
journalctl -u ton-monitor -n 50
```

### Getting Help

1. Check service status: `systemctl status ton-monitor`
2. View logs: `journalctl -u ton-monitor -f`
3. Test API: `curl http://localhost:8080/api/stats`
4. Verify configuration: `cat .env`

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check if service is running
curl http://your-server:8080/api/stats

# Expected response:
# {"total_transactions": 42, "total_amount": 125.5, ...}
```

### Database Backup

```bash
# Backup database
cp /opt/ton-monitor/transactions.db /opt/ton-monitor/backup_$(date +%Y%m%d).db

# Automated daily backup (add to crontab)
0 2 * * * cp /opt/ton-monitor/transactions.db /opt/ton-monitor/backup_$(date +\%Y\%m\%d).db
```

### Log Monitoring

```bash
# View recent logs
journalctl -u ton-monitor -n 100

# Follow logs in real-time
journalctl -u ton-monitor -f

# Check for errors
journalctl -u ton-monitor | grep -i error
```

## 🎯 Summary

1. **Install**: `pip install flask flask-cors requests python-dotenv`
2. **Configure**: Edit `.env` with your wallet address
3. **Run**: `python app_simple.py`
4. **Access**: Replace `localhost` with your server IP for remote access
5. **Integrate**: Use API endpoints in your applications
6. **Monitor**: Check dashboard and logs regularly

Your TON wallet monitor is now ready to detect genuine TON payments and provide API access for your applications!
