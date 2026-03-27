# 📊 داشبورد حركة المخزون

داشبورد تفاعلي لتتبع المخزون اليومي مع بيانات تاريخية متراكمة.

## 🗂️ هيكل المشروع

```
stock-dashboard/
├── data/                          ← ارفع ملفات Excel هنا يومياً
│   └── TotalStockQuantity2026_03_18.xlsx
├── docs/                          ← ملفات الموقع (GitHub Pages)
│   ├── index.html
│   ├── products.html
│   └── history.json               ← يتحدث تلقائياً
├── scripts/
│   └── process_excel.py           ← السكريبت الذي يعالج Excel
└── .github/workflows/
    └── process-stock.yml          ← GitHub Actions
```

## ⚙️ الإعداد الأول (مرة واحدة)

### 1. فعّل GitHub Pages
- اذهب إلى **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: **main** → مجلد: **`/docs`**
- احفظ

### 2. فعّل GitHub Actions
- اذهب إلى **Settings → Actions → General**
- تأكد أن **"Allow all actions"** مفعّل
- في **Workflow permissions** → اختر **"Read and write permissions"**

---

## 📅 الاستخدام اليومي

### الطريقة: رفع الملف مباشرة على GitHub

1. افتح الـ repo على GitHub
2. اضغط على مجلد **`data/`**
3. اضغط **"Add file" → "Upload files"**
4. ارفع ملف اليوم: `TotalStockQuantity2026_03_XX.xlsx`
5. اضغط **"Commit changes"**
6. **GitHub Actions يشتغل تلقائياً** (30-60 ثانية)
7. افتح الداشبورد — البيانات محدّثة ✅

> ⚠️ **مهم:** اسم الملف يجب أن يحتوي على التاريخ بالصيغة: `YYYY_MM_DD`
> مثال صحيح: `TotalStockQuantity2026_03_26.xlsx`

---

## 📊 ميزات الداشبورد

- **تطور تاريخي** — رسم بياني يعرض تطور المخزون عبر كل الأيام
- **مقارنة يومية** — التغيير بين كل يوم والسابق
- **جدول الأيام** — سجل كامل بكل الأيام
- **تفاصيل المنتجات** — عرض كل منتج مع توزيع المستودعات
- **فلترة** — بالفئة، الحالة، المستودع

---

## 🔧 متطلبات ملف Excel

يجب أن يحتوي الملف على الشيتات التالية:
- `المستودعات الرئيسية` ← **إلزامي**
- `المستودعات الفرعية` ← اختياري
- `المستودعات التالفة` ← اختياري
