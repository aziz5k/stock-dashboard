import os, json, re
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT = Path("docs/history.json")

WH_COLS = {
    "RIYADH_WAREHOUSE_DEFAA": "الرياض",
    "QASSIM_WAREHOUSE_NEW": "القصيم",
    "DAMMAM_WAREHOUSE_DAMMAM": "الدمام",
    "JEDDAH_WAREHOUSE_JEDDAH": "جدة",
    "KHAMIS_WAREHOUSE_KHAMIS": "خميس مشيط",
    "Main_Warehouse_Transit": "ترانزيت",
    "Purchasing_Warehouse": "مشتريات",
}

DMG_COLS = {
    "Riyadh_Warehouse_Defaa_Damage": "الرياض",
    "Qassim_Warehouse_Esilan_Damage": "القصيم إيسلان",
    "Qassim_Warehouse_NEW_Damage": "القصيم",
    "Dammam_Warehouse_Damage": "الدمام",
    "Jeddah_Warehouse_Damage": "جدة",
    "Khamis_Warehouse_Damage": "خميس مشيط",
    "Riyadh_Warehouse_Online_Damage": "الرياض أونلاين",
}

def classify(code, name):
    if re.match(r'^(AGT|AT)', code): return "شاي ومشروبات"
    if re.match(r'^DA', code): return "منظفات"
    if re.match(r'^HR', code): return "أرز"
    if any(x in name for x in ["فحم بخور","فحم سداسي","فحم فيتنامي","فحم شواء"]): return "فحم"
    if "حطب" in name: return "حطب"
    if any(x in name for x in ["ولاعة","اللهب"]): return "ولاعات"
    if any(x in name for x in ["لوفت","ستاند","حقيبة"]): return "إكسسوارات"
    if any(x in name for x in ["شنطة","منقل"]): return "معدات"
    return "متنوع"

def parse_file(path):
    fname = path.name
    m = re.search(r'(\d{4})_(\d{2})_(\d{2})', fname)
    if not m:
        print(f"⚠️  تجاهل {fname} — اسم غير مطابق للنمط")
        return None
    year, month, day = m.groups()
    date_key = f"{year}-{month}-{day}"
    date_label = f"{int(day)} / {int(month)} / {year}"

    try:
        sheets = pd.read_excel(path, sheet_name=None, header=None)
    except Exception as e:
        print(f"❌ خطأ في {fname}: {e}")
        return None

    # المستودعات الرئيسية
    main_sheet = sheets.get("المستودعات الرئيسية")
    if main_sheet is None:
        print(f"⚠️  {fname}: لا يوجد شيت 'المستودعات الرئيسية'")
        return None

    main_sheet.columns = main_sheet.iloc[0]
    main_sheet = main_sheet.iloc[1:].reset_index(drop=True)
    main_sheet = main_sheet[~main_sheet["ItemNo"].astype(str).str.startswith("~")]

    products = []
    main_total = 0
    wh_totals = {}

    for _, row in main_sheet.iterrows():
        code = str(row.get("ItemNo", "")).strip()
        if not code: continue
        name = str(row.get("ItemDescription", "")).strip()
        total = float(row.get("Total", 0) or 0)
        main_total += total

        warehouses = {}
        for col, ar in WH_COLS.items():
            val = float(row.get(col, 0) or 0)
            if val > 0:
                warehouses[ar] = round(val, 2)
                wh_totals[ar] = round(wh_totals.get(ar, 0) + val, 2)

        status = "نفد" if total == 0 else ("منخفض" if total < 5 else "نشط")
        products.append({
            "code": code,
            "name": name,
            "category": classify(code, name),
            "totalStock": round(total, 2),
            "status": status,
            "warehouses": warehouses,
        })

    # المستودعات التالفة
    dmg_total = 0
    dmg_sheet = sheets.get("المستودعات التالفة")
    dmg_products = []
    if dmg_sheet is not None:
        dmg_sheet.columns = dmg_sheet.iloc[0]
        dmg_sheet = dmg_sheet.iloc[1:].reset_index(drop=True)
        dmg_sheet = dmg_sheet[~dmg_sheet["ItemNo"].astype(str).str.startswith("~")]

        for _, row in dmg_sheet.iterrows():
            code = str(row.get("ItemNo", "")).strip()
            if not code: continue
            name = str(row.get("ItemDescription", "")).strip() + " (تالف)"
            total = float(row.get("Total", 0) or 0)
            dmg_total += total

            warehouses = {}
            for col, ar in DMG_COLS.items():
                val = float(row.get(col, 0) or 0)
                if val > 0:
                    warehouses[ar] = round(val, 2)

            dmg_products.append({
                "code": "DMG-" + code,
                "name": name,
                "category": "مخزون تالف",
                "totalStock": round(total, 2),
                "status": "تالف",
                "warehouses": warehouses,
            })

    print(f"✅ {fname}: {len(products)} منتج، مجموع {round(main_total,2):,}، تالف {round(dmg_total,2):,}")

    return {
        "dateKey": date_key,
        "dateLabel": date_label,
        "fileName": fname,
        "mainTotal": round(main_total, 2),
        "damagedTotal": round(dmg_total, 2),
        "warehouseTotals": wh_totals,
        "products": products,
        "damagedProducts": dmg_products,
    }

def main():
    xlsx_files = sorted(DATA_DIR.glob("*.xlsx")) + sorted(DATA_DIR.glob("*.xls"))
    if not xlsx_files:
        print("⚠️  لا توجد ملفات Excel في مجلد data/")
        return

    print(f"📂 وجدت {len(xlsx_files)} ملف")

    # تحميل التاريخ الموجود إن وجد
    existing = {}
    if OUTPUT.exists():
        try:
            existing = {d["dateKey"]: d for d in json.loads(OUTPUT.read_text(encoding="utf-8"))}
        except:
            pass

    for f in xlsx_files:
        result = parse_file(f)
        if result:
            existing[result["dateKey"]] = result

    # ترتيب حسب التاريخ
    history = sorted(existing.values(), key=lambda x: x["dateKey"])

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n🎉 history.json محدث: {len(history)} يوم")

if __name__ == "__main__":
    main()
