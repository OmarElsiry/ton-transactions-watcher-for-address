#!/usr/bin/env python3
"""
Cleanup script to remove duplicate files and organize the project
"""
import os
import shutil
from pathlib import Path

def cleanup_duplicates():
    """Remove duplicate files and organize project structure"""
    
    project_root = Path(__file__).parent
    
    # Files to remove (duplicates)
    files_to_remove = [
        'test_api.py',           # Replaced by test_complete.py
        'test_enhanced_sync.py', # Replaced by test_complete.py
        'app.py',                # Replaced by app_api.py
        'app_simple.py'          # Replaced by app_api.py
    ]
    
    # Backup directory
    backup_dir = project_root / 'backup_old_files'
    backup_dir.mkdir(exist_ok=True)
    
    print("🧹 Cleaning up duplicate files...")
    
    for filename in files_to_remove:
        file_path = project_root / filename
        
        if file_path.exists():
            # Move to backup instead of deleting
            backup_path = backup_dir / filename
            shutil.move(str(file_path), str(backup_path))
            print(f"   Moved {filename} to backup/")
        else:
            print(f"   {filename} not found (already removed)")
    
    print("\n✅ Cleanup completed!")
    print(f"📁 Old files backed up to: {backup_dir}")
    
    # Show current project structure
    print("\n📋 Current project structure:")
    print("   app_api.py          - Main API backend for external integration")
    print("   test_complete.py    - Unified testing script")
    print("   API_EXTERNAL.md     - External API documentation")
    print("   backup_old_files/   - Backup of removed duplicates")

if __name__ == '__main__':
    cleanup_duplicates()
