# TON Wallet Monitor - External API Documentation

## Overview

This API allows external websites and applications to integrate with the TON Wallet Monitor backend with **manual control** to verify transactions, check balances, and retrieve transaction data for a monitored TON wallet.

**Base URL:** `http://localhost:8080` (or your deployed URL)

**CORS:** Enabled for all origins - supports cross-origin requests from web browsers

**Authentication:** None required (public API)

**Operation Mode:** Manual sync only - no automatic polling

## Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "data": {...},
  "error": "error message if success=false",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API is running and get system information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "api_type": "tonapi",
  "monitored_wallet": "UQA..."
}
```

### 2. Get Transactions

**GET** `/api/transactions`

Retrieve transactions with optional filtering.

**Query Parameters:**
- `limit` (integer, optional): Number of transactions to return (max 1000, default 10)
- `min_amount` (float, optional): Minimum transaction amount in TON
- `max_amount` (float, optional): Maximum transaction amount in TON
- `sender_address` (string, optional): Filter by sender address
- `from_date` (string, optional): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `to_date` (string, optional): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)

**Example Request:**
```
GET /api/transactions?limit=50&min_amount=1.0&from_date=2024-01-01
```

**Response:**
```json
{
  "success": true,
  "count": 25,
  "transactions": [
    {
      "tx_hash": "abc123...",
      "amount_ton": "5.50",
      "sender_address": "UQB...",
      "recipient_address": "UQA...",
      "formatted_time": "2024-01-01 12:30:45",
      "timestamp": 1704110445,
      "message": "Payment for service",
      "confirmed": true
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 3. Get Balance

**GET** `/api/balance`

Get current wallet balance.

**Response:**
```json
{
  "success": true,
  "balance": {
    "balance_ton": 123.45,
    "balance_nanotons": 123450000000,
    "status": "active"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 4. Get Statistics

**GET** `/api/stats`

Get transaction statistics for the monitored wallet.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_transactions": 150,
    "total_amount": 1234.56,
    "average_amount": 8.23,
    "latest_transaction": "2024-01-01 12:30:45"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 5. Sync Transactions

**POST** `/api/sync`

Manually trigger synchronization of new transactions from the blockchain.

**Request Body:**
```json
{
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "new_transactions": 3,
  "message": "Found 3 new transactions",
  "transactions": [...],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 6. Verify Transaction

**GET** `/api/verify/transaction/<tx_hash>`

Verify if a specific transaction exists in the monitored wallet.

**Example Request:**
```
GET /api/verify/transaction/abc123def456...
```

**Response:**
```json
{
  "success": true,
  "verified": true,
  "transaction": {
    "tx_hash": "abc123...",
    "amount_ton": "5.50",
    "sender_address": "UQB...",
    "formatted_time": "2024-01-01 12:30:45",
    "confirmed": true
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 7. Verify Payment

**GET** `/api/verify/payment`

Verify payment by amount and timeframe - useful for payment verification systems.

**Query Parameters:**
- `amount` (float, required): Expected payment amount in TON
- `sender` (string, optional): Expected sender address
- `minutes_ago` (integer, optional): How many minutes back to search (default 60)

**Example Request:**
```
GET /api/verify/payment?amount=5.50&sender=UQB...&minutes_ago=30
```

**Response:**
```json
{
  "success": true,
  "verified": true,
  "payment_count": 1,
  "payments": [
    {
      "tx_hash": "abc123...",
      "amount_ton": "5.50",
      "sender_address": "UQB...",
      "formatted_time": "2024-01-01 12:30:45"
    }
  ],
  "search_criteria": {
    "amount": 5.50,
    "sender": "UQB...",
    "minutes_ago": 30
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 8. Get Wallet Info

**GET** `/api/wallet/info`

Get complete wallet information including balance, stats, and account details.

**Response:**
```json
{
  "success": true,
  "wallet_address": "UQA...",
  "account_info": {
    "balance": 123450000000,
    "state": "active"
  },
  "balance": {
    "balance_ton": 123.45
  },
  "stats": {
    "total_transactions": 150,
    "total_amount": 1234.56
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Integration Examples

### JavaScript/Frontend Integration

```javascript
// Check if a payment was received
async function verifyPayment(expectedAmount, senderAddress) {
  try {
    const response = await fetch(`http://localhost:8080/api/verify/payment?amount=${expectedAmount}&sender=${senderAddress}&minutes_ago=10`);
    const data = await response.json();
    
    if (data.success && data.verified) {
      console.log('Payment verified!', data.payments);
      return true;
    } else {
      console.log('Payment not found');
      return false;
    }
  } catch (error) {
    console.error('API Error:', error);
    return false;
  }
}

// Get recent transactions
async function getRecentTransactions() {
  try {
    const response = await fetch('http://localhost:8080/api/transactions?limit=20');
    const data = await response.json();
    
    if (data.success) {
      return data.transactions;
    }
  } catch (error) {
    console.error('API Error:', error);
  }
  return [];
}
```

### PHP Integration

```php
<?php
function verifyTONPayment($amount, $senderAddress = null, $minutesAgo = 60) {
    $url = "http://localhost:8080/api/verify/payment?amount=" . $amount . "&minutes_ago=" . $minutesAgo;
    
    if ($senderAddress) {
        $url .= "&sender=" . urlencode($senderAddress);
    }
    
    $response = file_get_contents($url);
    $data = json_decode($response, true);
    
    return $data['success'] && $data['verified'];
}

// Usage
if (verifyTONPayment(5.50, "UQB...")) {
    echo "Payment confirmed!";
} else {
    echo "Payment not found";
}
?>
```

### Python Integration

```python
import requests

class TONMonitorClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def verify_payment(self, amount, sender=None, minutes_ago=60):
        params = {
            'amount': amount,
            'minutes_ago': minutes_ago
        }
        if sender:
            params['sender'] = sender
            
        response = requests.get(f"{self.base_url}/api/verify/payment", params=params)
        data = response.json()
        
        return data.get('success', False) and data.get('verified', False)
    
    def get_transactions(self, limit=10, **filters):
        params = {'limit': limit, **filters}
        response = requests.get(f"{self.base_url}/api/transactions", params=params)
        data = response.json()
        
        if data.get('success'):
            return data.get('transactions', [])
        return []

# Usage
client = TONMonitorClient()
if client.verify_payment(5.50):
    print("Payment verified!")
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

Error responses include details:

```json
{
  "success": false,
  "error": "Amount parameter is required",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Rate Limiting

Currently no rate limiting is implemented, but consider implementing it for production use.

## Security Notes

1. This API is designed for read-only operations
2. No sensitive wallet keys are exposed
3. CORS is enabled for browser integration
4. Consider adding authentication for production deployments
5. Monitor API usage and implement rate limiting as needed

## Deployment

For production deployment:

1. Change `FLASK_HOST` and `FLASK_PORT` in config
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper logging and monitoring
4. Consider adding API authentication
5. Implement rate limiting
6. Use HTTPS in production
