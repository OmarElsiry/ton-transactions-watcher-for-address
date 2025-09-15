import requests
import json

def test_enhanced_sync():
    # Test the enhanced sync endpoint
    response = requests.post('http://localhost:8080/api/sync', json={'limit': 11})
    data = response.json()

    print('=== ENHANCED SYNC API RESPONSE ===')
    print(f'Status: {data["status"]}')
    print(f'New Transactions: {data["new_transactions"]}')
    print(f'Message: {data["message"]}')
    print()
    print('=== TRANSACTION DETAILS ===')
    for i, tx in enumerate(data.get('transactions', []), 1):
        print(f'Transaction {i}:')
        print(f'  Hash: {tx["tx_hash"][:20]}...')
        print(f'  Amount: {tx["amount_ton"]} TON')
        print(f'  From: {tx["sender_address"][:25]}...')
        print(f'  Time: {tx["formatted_time"]}')
        print(f'  Message: {tx.get("message", "None")}')
        print()

if __name__ == '__main__':
    test_enhanced_sync()
