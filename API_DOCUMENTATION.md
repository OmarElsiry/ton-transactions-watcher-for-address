# TON Wallet Monitor - API Documentation

Complete API reference for the TON Wallet Monitor service with detailed endpoints, parameters, and examples.

## 🌐 Base URL

```
Local Development: http://localhost:8080
Production: http://your-server-ip:8080
```

## 📋 Table of Contents

- [Authentication](#authentication)
- [Endpoints Overview](#endpoints-overview)
- [Transaction Endpoints](#transaction-endpoints)
- [Balance Endpoints](#balance-endpoints)
- [Statistics Endpoints](#statistics-endpoints)
- [Sync Endpoints](#sync-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Integration Examples](#integration-examples)

## 🔐 Authentication

**No authentication required** - All endpoints are publicly accessible. For production use, consider implementing API keys or IP whitelisting.

## 📊 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard web interface |
| GET | `/api/transactions` | Get transactions with filters |
| GET | `/api/balance` | Get wallet balance |
| GET | `/api/stats` | Get transaction statistics |
| POST | `/api/sync` | Manual blockchain sync |

---

## 💸 Transaction Endpoints

### GET /api/transactions

Retrieve transactions with optional filtering and pagination.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Number of transactions to return (max: 100) |
| `min_amount` | float | No | - | Minimum TON amount filter |
| `max_amount` | float | No | - | Maximum TON amount filter |
| `sender_address` | string | No | - | Filter by sender wallet address (partial match) |
| `from_date` | string | No | - | Start date filter (YYYY-MM-DD format) |
| `to_date` | string | No | - | End date filter (YYYY-MM-DD format) |

**Example Requests:**

```bash
# Get last 10 transactions
GET /api/transactions

# Get transactions over 1 TON
GET /api/transactions?min_amount=1.0

# Get transactions from specific sender
GET /api/transactions?sender_address=UQAbc123def456

# Get transactions in date range
GET /api/transactions?from_date=2024-01-01&to_date=2024-01-31

# Combined filters
GET /api/transactions?min_amount=0.5&max_amount=10.0&limit=50&from_date=2024-01-01
```

**Response Format:**

```json
[
  {
    "tx_hash": "a1b2c3d4e5f6789012345678901234567890abcdef",
    "account_id": "UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315",
    "sender_address": "UQAbc123def456ghi789jkl012mno345pqr678stu901vwx234",
    "sender_name": null,
    "amount_ton": 2.5,
    "amount_nanoton": 2500000000,
    "message": "Payment for service",
    "timestamp": 1704067200,
    "formatted_time": "2024-01-01 12:00:00",
    "block_number": 12345678,
    "confirmed": true,
    "processed": true
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tx_hash` | string | Unique transaction hash |
| `account_id` | string | Monitored wallet address |
| `sender_address` | string | Sender wallet address |
| `sender_name` | string | Sender name (if available) |
| `amount_ton` | float | Transaction amount in TON |
| `amount_nanoton` | integer | Transaction amount in nanoTON |
| `message` | string | Transaction message/memo |
| `timestamp` | integer | Unix timestamp |
| `formatted_time` | string | Human-readable timestamp |
| `block_number` | integer | Blockchain block number |
| `confirmed` | boolean | Transaction confirmation status |
| `processed` | boolean | Processing status |

---

## 💰 Balance Endpoints

### GET /api/balance

Get current wallet balance from the blockchain.

**Parameters:** None

**Example Request:**

```bash
GET /api/balance
```

**Response Format:**

```json
{
  "balance_ton": 125.75,
  "balance_nanoton": 125750000000,
  "address": "UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315",
  "last_updated": 1704067200,
  "status": "active"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `balance_ton` | float | Current balance in TON |
| `balance_nanoton` | integer | Current balance in nanoTON |
| `address` | string | Wallet address |
| `last_updated` | integer | Last update timestamp |
| `status` | string | Wallet status (active/inactive) |

---

## 📈 Statistics Endpoints

### GET /api/stats

Get comprehensive transaction statistics.

**Parameters:** None

**Example Request:**

```bash
GET /api/stats
```

**Response Format:**

```json
{
  "total_transactions": 156,
  "total_amount": 1250.75,
  "processed_count": 156,
  "average_amount": 8.02,
  "largest_transaction": 100.0,
  "smallest_transaction": 0.1,
  "first_transaction_date": "2024-01-01 10:30:00",
  "last_transaction_date": "2024-01-15 14:20:00",
  "unique_senders": 45,
  "transactions_today": 12,
  "amount_today": 45.5
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_transactions` | integer | Total number of transactions |
| `total_amount` | float | Total amount received (TON) |
| `processed_count` | integer | Number of processed transactions |
| `average_amount` | float | Average transaction amount |
| `largest_transaction` | float | Largest single transaction |
| `smallest_transaction` | float | Smallest single transaction |
| `first_transaction_date` | string | Date of first transaction |
| `last_transaction_date` | string | Date of last transaction |
| `unique_senders` | integer | Number of unique senders |
| `transactions_today` | integer | Transactions received today |
| `amount_today` | float | Amount received today |

---

## 🔄 Sync Endpoints

### POST /api/sync

Manually trigger blockchain synchronization to fetch new transactions. **Enhanced response includes complete transaction data.**

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of transactions to fetch |

**Request Body:**

```json
{
  "limit": 20
}
```

**Example Request:**

```bash
curl -X POST http://localhost:8080/api/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'
```

**Enhanced Response Format:**

```json
{
  "status": "success",
  "new_transactions": 3,
  "message": "Found 3 new transactions",
  "transactions": [
    {
      "tx_hash": "HtD71OYE0F2JjKd2FlgvFSt4WdAeMbw=",
      "account_id": "UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315",
      "sender_address": "EQAOvLwrhnaqkW_e1Qu8oZc3XnIOx9Qzk07JSGedWBzlbeR",
      "sender_name": null,
      "amount_ton": 0.1,
      "amount_nanoton": 100000000,
      "message": "te6cckEBAQEAAgAAAEysuc0=",
      "timestamp": 1757884827,
      "formatted_time": "2025-09-15 01:00:14",
      "short_hash": "HtD71OYE0F...",
      "short_sender": "EQAOvLwrhn...",
      "block_number": null,
      "confirmed": true,
      "processed": false
    }
  ],
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Operation status (success/error) |
| `new_transactions` | integer | Number of new transactions found |
| `message` | string | Human-readable status message |
| `transactions` | array | Complete transaction objects with all details |

---

## ❌ Error Handling

All endpoints return consistent error responses with appropriate HTTP status codes.

**Error Response Format:**

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": 1704067200,
  "details": {
    "parameter": "invalid_value"
  }
}
```

**Common HTTP Status Codes:**

| Code | Description | Example |
|------|-------------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Server Error | Database or API error |

**Example Error Responses:**

```json
// Invalid parameter
{
  "error": "Invalid min_amount parameter",
  "code": "INVALID_PARAMETER",
  "timestamp": 1704067200
}

// Service unavailable
{
  "error": "Unable to connect to blockchain API",
  "code": "SERVICE_UNAVAILABLE",
  "timestamp": 1704067200
}
```

---

## ⚡ Rate Limiting

**Current Limits:**
- No rate limiting implemented
- Recommended: 100 requests per minute per IP

**Production Recommendations:**
- Implement rate limiting for public APIs
- Use caching for frequently accessed data
- Monitor API usage patterns

---

## 🔧 Integration Examples

### PHP Integration

```php
<?php
class TONMonitorAPI {
    private $baseUrl;
    
    public function __construct($baseUrl) {
        $this->baseUrl = rtrim($baseUrl, '/');
    }
    
    public function getTransactions($filters = []) {
        $url = $this->baseUrl . '/api/transactions';
        
        if (!empty($filters)) {
            $url .= '?' . http_build_query($filters);
        }
        
        $response = file_get_contents($url);
        return json_decode($response, true);
    }
    
    public function getBalance() {
        $url = $this->baseUrl . '/api/balance';
        $response = file_get_contents($url);
        return json_decode($response, true);
    }
    
    public function syncTransactions($limit = 10) {
        $url = $this->baseUrl . '/api/sync';
        $data = json_encode(['limit' => $limit]);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => $data
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        return json_decode($response, true);
    }
}

// Usage example
$api = new TONMonitorAPI('http://your-server:8080');

// Get recent transactions
$transactions = $api->getTransactions(['limit' => 20]);

// Get transactions over 1 TON
$bigTransactions = $api->getTransactions([
    'min_amount' => 1.0,
    'limit' => 50
]);

// Check wallet balance
$balance = $api->getBalance();
echo "Current balance: " . $balance['balance_ton'] . " TON\n";

// Manual sync
$syncResult = $api->syncTransactions(15);
echo "Found " . $syncResult['new_transactions'] . " new transactions\n";
?>
```

### JavaScript/Node.js Integration

```javascript
class TONMonitorAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async getTransactions(filters = {}) {
        const params = new URLSearchParams(filters);
        const url = `${this.baseUrl}/api/transactions?${params}`;
        
        const response = await fetch(url);
        return await response.json();
    }
    
    async getBalance() {
        const response = await fetch(`${this.baseUrl}/api/balance`);
        return await response.json();
    }
    
    async getStats() {
        const response = await fetch(`${this.baseUrl}/api/stats`);
        return await response.json();
    }
    
    async syncTransactions(limit = 10) {
        const response = await fetch(`${this.baseUrl}/api/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limit })
        });
        return await response.json();
    }
}

// Usage example
const api = new TONMonitorAPI('http://your-server:8080');

// Monitor for new payments
async function checkForPayments() {
    try {
        // Get transactions over 0.5 TON from last hour
        const transactions = await api.getTransactions({
            min_amount: 0.5,
            limit: 100
        });
        
        transactions.forEach(tx => {
            console.log(`Payment: ${tx.amount_ton} TON from ${tx.sender_address}`);
            // Process payment in your system
            processPayment(tx);
        });
        
    } catch (error) {
        console.error('Error checking payments:', error);
    }
}

// Check every 30 seconds
setInterval(checkForPayments, 30000);

// Real-time balance monitoring
async function monitorBalance() {
    const balance = await api.getBalance();
    console.log(`Current balance: ${balance.balance_ton} TON`);
    
    const stats = await api.getStats();
    console.log(`Total received: ${stats.total_amount} TON in ${stats.total_transactions} transactions`);
}
```

### Python Integration

```python
import requests
import time
from typing import Dict, List, Optional

class TONMonitorAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def get_transactions(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get transactions with optional filters"""
        url = f"{self.base_url}/api/transactions"
        
        response = requests.get(url, params=filters or {})
        response.raise_for_status()
        return response.json()
    
    def get_balance(self) -> Dict:
        """Get current wallet balance"""
        url = f"{self.base_url}/api/balance"
        
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict:
        """Get transaction statistics"""
        url = f"{self.base_url}/api/stats"
        
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def sync_transactions(self, limit: int = 10) -> Dict:
        """Manually sync transactions"""
        url = f"{self.base_url}/api/sync"
        
        response = requests.post(url, json={'limit': limit})
        response.raise_for_status()
        return response.json()

# Usage example
api = TONMonitorAPI('http://your-server:8080')

def monitor_payments():
    """Monitor for new payments"""
    try:
        # Get transactions over 1 TON
        transactions = api.get_transactions({
            'min_amount': 1.0,
            'limit': 50
        })
        
        for tx in transactions:
            print(f"Payment: {tx['amount_ton']} TON from {tx['sender_address']}")
            
            # Process payment
            process_payment(tx)
            
    except requests.RequestException as e:
        print(f"API Error: {e}")

def process_payment(transaction: Dict):
    """Process a payment in your system"""
    # Your payment processing logic here
    print(f"Processing payment: {transaction['tx_hash']}")

# Continuous monitoring
while True:
    monitor_payments()
    time.sleep(30)  # Check every 30 seconds
```

---

## 🛡️ Security Considerations

### Input Validation
- All parameters are validated and sanitized
- SQL injection protection through parameterized queries
- XSS protection in web interface

### Rate Limiting (Recommended)
```python
# Example rate limiting implementation
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/api/transactions')
@limiter.limit("50 per minute")
def get_transactions():
    # Your endpoint logic
    pass
```

### CORS Configuration
```python
# Production CORS setup
CORS(app, origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
])
```

---

## 📝 Changelog

### Version 1.0.0
- Initial API release
- Basic transaction filtering
- Balance and statistics endpoints
- Manual sync functionality

### Version 1.1.0 (Current)
- Enhanced filtering options
- Improved error handling
- Added comprehensive documentation
- Performance optimizations

---

## 🆘 Support

For API support and questions:
- Check the troubleshooting section in DEPLOYMENT_GUIDE.md
- Review error responses for debugging information
- Monitor server logs for detailed error messages

**Common Issues:**
- **Empty response**: Check if wallet has transactions
- **Connection errors**: Verify server is running and accessible
- **Invalid filters**: Review parameter formats and types
