#!/usr/bin/env python3
"""
Comprehensive Test Script for TON Wallet Monitor API
Combines functionality from test_api.py and test_enhanced_sync.py
"""
import requests
import datetime
import json
import time
import sys

class TONMonitorTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """Test if the API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                print("✅ API server is running")
                return True
            else:
                print(f"❌ API server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Make sure it's running on port 8080")
            return False
    
    def test_sync_endpoint(self, limit=10):
        """Test the enhanced sync endpoint (from test_enhanced_sync.py)"""
        print(f"\n=== TESTING SYNC ENDPOINT (limit={limit}) ===")
        try:
            response = self.session.post(f'{self.base_url}/api/sync', 
                                       json={'limit': limit})
            
            if response.status_code != 200:
                print(f"❌ Sync failed with status {response.status_code}")
                return None
                
            data = response.json()
            
            print(f'Status: {data["status"]}')
            print(f'New Transactions: {data["new_transactions"]}')
            print(f'Message: {data["message"]}')
            
            if data.get('transactions'):
                print('\n--- TRANSACTION DETAILS ---')
                for i, tx in enumerate(data['transactions'][:5], 1):  # Show first 5
                    print(f'Transaction {i}:')
                    print(f'  Hash: {tx["tx_hash"][:20]}...')
                    print(f'  Amount: {tx["amount_ton"]} TON')
                    print(f'  From: {tx["sender_address"][:25]}...')
                    print(f'  Time: {tx["formatted_time"]}')
                    print(f'  Message: {tx.get("message", "None")}')
                    print()
            
            return data
            
        except Exception as e:
            print(f"❌ Sync test failed: {e}")
            return None
    
    def test_transactions_endpoint(self):
        """Test transactions endpoint with various filters (from test_api.py)"""
        print("\n=== TESTING TRANSACTIONS ENDPOINT ===")
        
        # Get current time for filtering
        now = datetime.datetime.now()
        ten_seconds_ago = now - datetime.timedelta(seconds=10)
        six_hours_ago = now - datetime.timedelta(hours=6)
        
        # Test 1: Last 10 seconds
        print('\n--- LAST 10 SECONDS ---')
        try:
            response = self.session.get(f'{self.base_url}/api/transactions', params={
                'from_date': ten_seconds_ago.strftime('%Y-%m-%d'),
                'limit': 50
            })
            
            if response.status_code == 200:
                transactions_10s = response.json()
                print(f'Transactions in last 10 seconds: {len(transactions_10s)}')
                if transactions_10s:
                    for tx in transactions_10s[:3]:  # Show first 3
                        print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')
                else:
                    print('  No transactions found in last 10 seconds')
            else:
                print(f'❌ Request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing last 10 seconds: {e}')
        
        # Test 2: Last 6 hours
        print('\n--- LAST 6 HOURS ---')
        try:
            response = self.session.get(f'{self.base_url}/api/transactions', params={
                'from_date': six_hours_ago.strftime('%Y-%m-%d'),
                'limit': 100
            })
            
            if response.status_code == 200:
                transactions_6h = response.json()
                print(f'Transactions in last 6 hours: {len(transactions_6h)}')
                if transactions_6h:
                    for tx in transactions_6h[:5]:  # Show first 5
                        print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')
                else:
                    print('  No transactions found in last 6 hours')
            else:
                print(f'❌ Request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing last 6 hours: {e}')
        
        # Test 3: All recent transactions
        print('\n--- ALL RECENT TRANSACTIONS ---')
        try:
            response = self.session.get(f'{self.base_url}/api/transactions', 
                                      params={'limit': 10})
            
            if response.status_code == 200:
                all_transactions = response.json()
                print(f'Total recent transactions: {len(all_transactions)}')
                if all_transactions:
                    for tx in all_transactions:
                        print(f'  - {tx["amount_ton"]} TON from {tx["sender_address"][:20]}... at {tx["formatted_time"]}')
                else:
                    print('  No recent transactions found')
            else:
                print(f'❌ Request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing recent transactions: {e}')
    
    def test_balance_endpoint(self):
        """Test balance endpoint"""
        print("\n=== TESTING BALANCE ENDPOINT ===")
        try:
            response = self.session.get(f'{self.base_url}/api/balance')
            
            if response.status_code == 200:
                balance_data = response.json()
                print(f'✅ Balance: {balance_data.get("balance_ton", 0)} TON')
                if 'balance_nanotons' in balance_data:
                    print(f'   Nanotons: {balance_data["balance_nanotons"]}')
                if 'status' in balance_data:
                    print(f'   Account Status: {balance_data["status"]}')
            else:
                print(f'❌ Balance request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing balance: {e}')
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        print("\n=== TESTING STATS ENDPOINT ===")
        try:
            response = self.session.get(f'{self.base_url}/api/stats')
            
            if response.status_code == 200:
                stats = response.json()
                print(f'✅ Total Transactions: {stats.get("total_transactions", 0)}')
                print(f'   Total Amount: {stats.get("total_amount", 0)} TON')
                print(f'   Average Amount: {stats.get("average_amount", 0)} TON')
                if 'latest_transaction' in stats:
                    print(f'   Latest Transaction: {stats["latest_transaction"]}')
            else:
                print(f'❌ Stats request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing stats: {e}')
    
    def test_filters(self):
        """Test various transaction filters"""
        print("\n=== TESTING TRANSACTION FILTERS ===")
        
        # Test minimum amount filter
        print('\n--- FILTER: Min Amount 1.0 TON ---')
        try:
            response = self.session.get(f'{self.base_url}/api/transactions', 
                                      params={'min_amount': 1.0, 'limit': 10})
            
            if response.status_code == 200:
                filtered_txs = response.json()
                print(f'Transactions >= 1.0 TON: {len(filtered_txs)}')
                for tx in filtered_txs[:3]:
                    print(f'  - {tx["amount_ton"]} TON (✓ >= 1.0)')
            else:
                print(f'❌ Filter request failed with status {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error testing min amount filter: {e}')
    
    def run_complete_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Complete TON Monitor API Test Suite")
        print("=" * 60)
        
        # Check connection first
        if not self.test_connection():
            print("\n❌ Cannot proceed with tests - API server not accessible")
            return False
        
        # Run all test suites
        self.test_sync_endpoint(limit=11)
        self.test_transactions_endpoint()
        self.test_balance_endpoint()
        self.test_stats_endpoint()
        self.test_filters()
        
        print("\n" + "=" * 60)
        print("✅ Complete test suite finished!")
        return True

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TON Monitor API Test Suite')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='Base URL of the API server (default: http://localhost:8080)')
    parser.add_argument('--sync-only', action='store_true', 
                       help='Run only sync endpoint test')
    parser.add_argument('--transactions-only', action='store_true', 
                       help='Run only transactions endpoint tests')
    parser.add_argument('--limit', type=int, default=10, 
                       help='Limit for sync endpoint (default: 10)')
    
    args = parser.parse_args()
    
    tester = TONMonitorTester(base_url=args.url)
    
    if args.sync_only:
        tester.test_sync_endpoint(limit=args.limit)
    elif args.transactions_only:
        tester.test_transactions_endpoint()
    else:
        tester.run_complete_test()

if __name__ == '__main__':
    main()
