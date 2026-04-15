import pandas as pd
import json
import os
from datetime import datetime

# CLEANING HELPER
def clean_numeric(val):
    if pd.isna(val) or val == 'nothing' or val == '-':
        return 0
    try:
        if isinstance(val, str):
            val = val.replace(',', '').replace('SAR', '').strip()
        return float(val)
    except:
        return 0

def clean_date(val):
    if pd.isna(val) or val == 'nothing' or val == '-':
        return "Not Specified"
    try:
        dt = pd.to_datetime(val)
        return dt.strftime('%Y-%m-%d')
    except:
        return str(val)

def process_excel(file_path):
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)
    
    tenders = []
    for _, row in df.iterrows():
        tenders.append({
            "id": str(row.get('Tender ID', 'N/A')),
            "ref": str(row.get('Reference Number', 'N/A')),
            "title": str(row.get('Competition title', 'Unnamed Tender')),
            "org": str(row.get('Foundation', 'Not Specified')),
            "branch": str(row.get('Branch', 'Not Specified')),
            "status": str(row.get('the condition', 'Certified')),
            "city": str(row.get('City', 'Not Specified')),
            "area": str(row.get('Area', 'Not Specified')),
            "activity": str(row.get('Activity', 'Not Specified')),
            "type": str(row.get('Type of competition', 'Public')),
            "cost": clean_numeric(row.get('Cost of competition papers', 0)),
            "value": clean_numeric(row.get('The award value', 0)),
            "pub_date": clean_date(row.get('Publication date')),
            "deadline": clean_date(row.get('Deadline for submitting offers')),
            "days_left": int(row.get('How many days are left?', 0)) if pd.notna(row.get('How many days are left?')) else 0,
            "supplier": str(row.get('Supplier name', 'N/A')),
            "link": str(row.get('the details', '#')),
            "goal": str(row.get('Competition goal', ''))
        })
    
    return tenders

def main():
    source_file = r'D:\translated_large.xlsx'
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found.")
        return

    data = process_excel(source_file)
    output_file = 'tenders_data.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully processed {len(data)} tenders.")

    # Git Sync (Optional/Context dependent)
    try:
        import subprocess
        remotes = subprocess.check_output(['git', 'remote']).decode().split()
        if 'origin' in remotes:
            subprocess.run(['git', 'add', output_file], check=True)
            subprocess.run(['git', 'commit', '-m', f"Data sync {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], check=True)
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            print("✅ Data synced and deployed live to the dashboard!")
    except Exception as e:
        print(f"⚠️ Git sync skipped: {e}")

if __name__ == "__main__":
    main()
