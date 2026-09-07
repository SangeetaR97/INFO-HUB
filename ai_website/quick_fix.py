"""
Quick Fix Script for Data.csv
Run this to automatically fix common issues
"""

import pandas as pd

print("🔧 Quick Fix for Data.csv")
print("="*50)

try:
    # Read CSV
    df = pd.read_csv("Data.csv")
    print(f"✓ Loaded {len(df)} rows")
    
    original_count = len(df)
    
    # Fix 1: Remove duplicate header rows
    df = df[df['status'] != 'status']
    print(f"✓ Removed duplicate headers")
    
    # Fix 2: Remove NaN values
    df = df.dropna(subset=['statement', 'status'])
    print(f"✓ Removed NaN values")
    
    # Fix 3: Remove empty strings
    df = df[(df['statement'].str.strip() != '') & (df['status'].str.strip() != '')]
    print(f"✓ Removed empty strings")
    
    # Fix 4: Standardize status labels
    df['status'] = df['status'].str.strip().str.title()
    print(f"✓ Standardized status labels")
    
    # Fix 5: Keep only valid statuses
    valid_statuses = ['Normal', 'Depression', 'Anxiety', 'Stress']
    df = df[df['status'].isin(valid_statuses)]
    print(f"✓ Filtered to valid statuses")
    
    # Show results
    print(f"\n📊 Results:")
    print(f"   Before: {original_count} rows")
    print(f"   After:  {len(df)} rows")
    print(f"   Removed: {original_count - len(df)} invalid rows")
    
    print(f"\n📈 Class Distribution:")
    for status, count in df['status'].value_counts().items():
        print(f"   {status:12s}: {count:4d} samples")
    
    # Save backup
    print(f"\n💾 Saving backup to Data_backup.csv...")
    original_df = pd.read_csv("Data.csv")
    original_df.to_csv("Data_backup.csv", index=False)
    print(f"   ✓ Backup saved")
    
    # Save cleaned data
    print(f"\n💾 Saving cleaned data to Data.csv...")
    df.to_csv("Data.csv", index=False)
    print(f"   ✓ Cleaned data saved")
    
    print(f"\n{'='*50}")
    print("✅ SUCCESS! Your Data.csv is now clean.")
    print(f"{'='*50}")
    print("\nNow run: python app.py")
    
except FileNotFoundError:
    print("❌ Error: Data.csv not found!")
    print("   Make sure Data.csv is in the same folder as this script")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()