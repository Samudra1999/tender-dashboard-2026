import pandas as pd
import re
import json
import os
from datetime import datetime

def extract_field(text, patterns):
    if not isinstance(text, str):
        return "غير محدد"
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "غير محدد"

def process_excel(file_path):
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)
    
    # Cleaning columns
    df['اخر موعد لتقديم العروض'] = pd.to_datetime(df['اخر موعد لتقديم العروض'], errors='coerce')
    
    # Patterns for extraction
    city_patterns = [r'المدينة\s+([^،]+)', r'مدينة\s+([^،]+)', r'في\s+([^،]+)', r'المنطقة\s+([^،]+)']
    activity_patterns = [r'ونشاط المنافسة هو\s+([^.]+)', r'النشاط الرئيسي\s+([^.]+)']
    
    tenders = []
    for _, row in df.iterrows():
        details = str(row.get('تفاصيل المنافسة', ''))
        
        # Calculate status based on date
        deadline = row.get('اخر موعد لتقديم العروض')
        days_left = row.get('باقي كم يوم', 0)
        
        tender = {
            "id": str(row.get('Tender ID', 'N/A')),
            "title": str(row.get('عنوان المنافسة', 'منافسة غير معنونة')),
            "org": str(row.get('الفرع', '')) if pd.notna(row.get('الفرع')) else str(row.get('المؤسسة', 'غير محدد')),
            "status": str(row.get('الحالة', 'معتمدة')),
            "city": extract_field(details, city_patterns),
            "activity": extract_field(details, activity_patterns),
            "cost": float(row.get('تكلفة اوراق المنافسة', 0)) if pd.notna(row.get('تكلفة اوراق المنافسة')) else 0,
            "deadline": deadline.strftime('%Y-%m-%d') if pd.notna(deadline) else "غير محدد",
            "days_left": int(days_left) if pd.notna(days_left) else 0,
            "link": str(row.get('التفاصيل', '#'))
        }
        tenders.append(tender)
    
    return tenders

def main():
    source_file = r'D:\tenders-2026-04-13-q4770su2 (1).xlsx'
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found.")
        return

    data = process_excel(source_file)
    output_file = 'tenders_data.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully processed {len(data)} tenders.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
