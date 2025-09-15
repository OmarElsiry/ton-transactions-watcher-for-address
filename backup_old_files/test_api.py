import requests
import datetime

def test_transactions():
    # Get current time and calculate timestamps
    now = datetime.datetime.now()
    ten_seconds_ago = now - datetime.timedelta(seconds=10)
    six_hours_ago = now - datetime.timedelta(hours=6)

    print('=== TESTING LAST 10 SECONDS ===')
    # Test last 10 seconds transactions
    response = requests.get('http://localhost:8080/api/transactions', params={
        'from_date': ten_seconds_ago.strftime('%Y-%m-%d'),
        'limit': 50
    })
    transactions_10s = response.json()
    print(f'Transactions in last 10 seconds: {len(transactions_10s)}')
    if transactions_10s:
        for tx in transactions_10s[:3]:  # Show first 3
            print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')
    else:
        print('  No transactions found in last 10 seconds')

    print('\n=== TESTING LAST 6 HOURS ===')
    # Test last 6 hours transactions  
    response = requests.get('http://localhost:8080/api/transactions', params={
        'from_date': six_hours_ago.strftime('%Y-%m-%d'),
        'limit': 100
    })
    transactions_6h = response.json()
    print(f'Transactions in last 6 hours: {len(transactions_6h)}')
    if transactions_6h:
        for tx in transactions_6h[:5]:  # Show first 5
            print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')
    else:
        print('  No transactions found in last 6 hours')

    print('\n=== ALL RECENT TRANSACTIONS ===')
    # Get all recent transactions
    response = requests.get('http://localhost:8080/api/transactions', params={'limit': 10})
    all_transactions = response.json()
    print(f'Total recent transactions: {len(all_transactions)}')
    if all_transactions:
        for tx in all_transactions:
            print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')

if __name__ == '__main__':
    test_transactions()
