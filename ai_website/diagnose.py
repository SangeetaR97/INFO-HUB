"""
Quick diagnosis of Data.csv problems
"""

import pandas as pd

print("\n🔍 DIAGNOSING Data.csv")
print("="*60)

try:
    df = pd.read_csv("Data.csv")
    
    print(f"\n1️⃣ File loaded: {len(df)} rows\n")
    
    # Check columns
    print(f"2️⃣ Columns: {list(df.columns)}")
    if 'statement' not in df.columns or 'status' not in df.columns:
        print("   ❌ PROBLEM: Missing required columns!")
    else:
        print("   ✓ Required columns present\n")
    
    # Check for 'status' in data
    print(f"3️⃣ Checking for duplicate headers in data...")
    status_in_data = (df['status'] == 'status').sum()
    if status_in_data > 0:
        print(f"   ❌ PROBLEM: Found {status_in_data} rows where status='status'")
        print(f"      (These are duplicate header rows)\n")
    else:
        print("   ✓ No duplicate headers\n")
    
    # Check NaN
    print(f"4️⃣ Checking for missing values...")
    statement_nan = df['statement'].isna().sum()
    status_nan = df['status'].isna().sum()
    if statement_nan > 0 or status_nan > 0:
        print(f"   ❌ PROBLEM: Missing values found!")
        print(f"      Statement NaN: {statement_nan}")
        print(f"      Status NaN: {status_nan}\n")
    else:
        print("   ✓ No missing values\n")
    
    # Check unique statuses
    print(f"5️⃣ Status values found:")
    unique_statuses = df['status'].dropna().unique()
    for status in unique_statuses:
        count = (df['status'] == status).sum()
        print(f"   '{status}': {count} rows")
    
    valid = ['Normal', 'Depression', 'Anxiety', 'Stress', 
             'normal', 'depression', 'anxiety', 'stress']
    invalid = [s for s in unique_statuses if s not in valid]
    if invalid:
        print(f"\n   ❌ PROBLEM: Invalid status values: {invalid}")
    else:
        print(f"\n   ✓ All status values are valid")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print("="*60)
    
    problems = []
    if 'statement' not in df.columns or 'status' not in df.columns:
        problems.append("Missing required columns")
    if status_in_data > 0:
        problems.append(f"{status_in_data} duplicate header rows")
    if statement_nan > 0 or status_nan > 0:
        problems.append(f"{statement_nan + status_nan} missing values")
    if invalid:
        problems.append(f"{len(invalid)} invalid status values")
    
    if problems:
        print("\n❌ PROBLEMS FOUND:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")
        print("\n🔧 FIX: Run 'python quick_fix.py' to fix automatically")
    else:
        print("\n✅ No problems found! Your CSV looks good.")
        print("   You can run 'python app.py' now")
    
    print("="*60 + "\n")
    
except FileNotFoundError:
    print("\n❌ ERROR: Data.csv not found!")
    print("   Make sure Data.csv is in this folder\n")
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")