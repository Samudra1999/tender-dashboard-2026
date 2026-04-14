import pandas as pd
import re
import json
import os
from datetime import datetime

# Translation Dictionaries
CITY_MAP = {
    "الرياض": "Riyadh",
    "جدة": "Jeddah",
    "الدمام": "Dammam",
    "مكة المكرمة": "Makkah",
    "المدينة المنورة": "Madinah",
    "الأحساء": "Al-Ahsa",
    "الطائف": "Taif",
    "خميس مشيط": "Khamis Mushait",
    "تبوك": "Tabuk",
    "بريدة": "Buraidah",
    "غير محدد": "Not Specified",
    "الخبر": "Al-Khobar",
    "الحفوف": "Hofuf"
}

STATUS_MAP = {
    "معتمدة": "Approved",
    "ملغي": "Cancelled",
    "منتهي": "Expired"
}

TITLE_KEYWORDS = [
    (r'^مشروع\s+', 'Project: '),
    (r'^توريد\s+', 'Supply of '),
    (r'^تأمين\s+', 'Provision of '),
    (r'^تشغيل وصيانة\s+', 'Operation & Maintenance of '),
    (r'^تجديد\s+', 'Renewal of '),
    (r'^توفير\s+', 'Providing '),
    (r'^تقديم خدمات\s+', 'Delivery of Services for '),
    (r'\s+بـ\s+', ' in '),
    (r'\s+لـ\s+', ' for '),
    (r'\s+و\s+', ' and '),
]

def translate_title(title):
    eng_title = title
    for ar_pat, en_sub in TITLE_KEYWORDS:
        eng_title = re.sub(ar_pat, en_sub, eng_title)
    
    # If it's still mostly Arabic characters, we can append a prefix or keep it
    # For a high-end dashboard, we aim for a hybrid if full translation is complex
    if any('\u0600' <= c <= '\u06FF' for c in eng_title):
        # Optional: Add "Project - " prefix for non-translated titles
        if not eng_title.startswith("Project:"):
            eng_title = "Tender: " + eng_title
            
    return eng_title

def translate_org(org):
    if "وزارة" in org: return f"Ministry of {org.replace('وزارة', '').strip()}"
    if "جامعة" in org: return f"University of {org.replace('جامعة', '').strip()}"
    if "مستشفى" in org: return f"Hospital of {org.replace('مستشفى', '').strip()}"
    if "أمانة" in org: return f"Municipality of {org.replace('أمانة', '').strip()}"
    if "الهيئة" in org: return f"Authority of {org.replace('الهيئة', '').strip()}"
    return org

def extract_field(text, patterns):
    if not isinstance(text, str):
        return "Not Specified"
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            val = match.group(1).strip()
            return CITY_MAP.get(val, val)
    return "Not Specified"

def process_excel(file_path):
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)
    
    # Cleaning columns
    df['اخر موعد لتقديم العروض'] = pd.to_datetime(df['اخر موعد لتقديم العروض'], errors='coerce')
    
    city_patterns = [r'المدينة\s+([^،]+)', r'مدينة\s+([^،]+)', r'في\s+([^،]+)', r'المنطقة\s+([^،]+)']
    activity_patterns = [r'ونشاط المنافسة هو\s+([^.]+)', r'النشاط الرئيسي\s+([^.]+)']
    
    tenders = []
    for _, row in df.iterrows():
        details = str(row.get('تفاصيل المنافسة', ''))
        
        deadline = row.get('اخر موعد لتقديم العروض')
        days_left = row.get('باقي كم يوم', 0)
        
        ar_org = str(row.get('الفرع', '')) if pd.notna(row.get('الفرع')) else str(row.get('المؤسسة', 'Not Specified'))
        ar_status = str(row.get('الحالة', 'معتمدة'))
        ar_title = str(row.get('عنوان المنافسة', 'Unnamed Tender'))
        
        tender = {
            "id": str(row.get('Tender ID', 'N/A')),
            "title": translate_title(ar_title),
            "org": translate_org(ar_org),
            "status": STATUS_MAP.get(ar_status, ar_status),
            "city": extract_field(details, city_patterns),
            "activity": "General" if "غير محدد" in str(row.get('النشاط', '')) else "IT/Tech", # Simplified for now
            "cost": float(row.get('تكلفة اوراق المنافسة', 0)) if pd.notna(row.get('تكلفة اوراق المنافسة')) else 0,
            "deadline": deadline.strftime('%Y-%m-%d') if pd.notna(deadline) else "Not Specified",
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
    
    print(f"Successfully processed {len(data)} tenders (Localized).")

    # Git Sync
    try:
        import subprocess
        remotes = subprocess.check_output(['git', 'remote']).decode().split()
        if 'origin' in remotes:
            subprocess.run(['git', 'add', output_file], check=True)
            subprocess.run(['git', 'commit', '-m', f"English localization sync {datetime.now()}"], check=True)
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            print("✅ Online Dashboard updated (English Data)!")
    except Exception as e:
        print(f"⚠️ Git sync skipped: {e}")

if __name__ == "__main__":
    main()
