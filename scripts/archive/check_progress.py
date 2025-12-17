#!/usr/bin/env python3
"""
Quick progress checker for data collection
"""
import os
import time

log_file = 'data_collection.log'

print("📊 Monitoring data collection progress...")
print("=" * 60)

while True:
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Get last 10 lines
        recent = lines[-10:] if len(lines) > 10 else lines
        
        print("\n" + "=" * 60)
        print(f"⏰ Last update: {time.strftime('%H:%M:%S')}")
        print("=" * 60)
        for line in recent:
            print(line.strip())
        
    time.sleep(60)  # Check every minute
