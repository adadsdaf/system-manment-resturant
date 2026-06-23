# دليل إعداد وتشغيل النظام
# Restaurant Management System - Setup & Run Guide

---

## 📋 نظرة عامة

نظام إدارة المطاعم المتكامل يدعم **قاعدتا بيانات**:
- **PostgreSQL** — لتطبيق الويب (Flask) ← **الوضع الافتراضي في Replit**
- **SQL Server / MSSQL** — لتطبيق سطح المكتب (PyQt6) ← يتطلب Windows + SQL Server

---

## 🚀 تشغيل تطبيق الويب (Flask + PostgreSQL)

### المتطلبات
```
Python 3.10+
PostgreSQL (متوفر تلقائيًا في Replit)
pip packages: flask, psycopg2-binary, bcrypt, Werkzeug
```

### خطوات التشغيل في Replit
1. **إنشاء قاعدة البيانات** (تلقائي عبر Replit Database)
2. **تطبيق المخطط** — يتم تلقائيًا عبر `database/schema.sql`
3. **تشغيل التطبيق**:
   ```bash
   python app.py
   ```
4. **الوصول**: فتح المتصفح على `http://0.0.0.0:5000`

### بيانات الدخول الافتراضية
| المستخدم | كلمة المرور | الدور |
|----------|-------------|-------|
| `admin` | `admin123` | مدير النظام |

---

## 🗄️ إعداد قاعدة البيانات PostgreSQL يدويًا

### تطبيق مخطط قاعدة البيانات
```bash
# في Replit (تلقائي)
psql $DATABASE_URL -f database/schema.sql

# أو عبر Python
python -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
with open('database/schema.sql') as f:
    cur.execute(f.read())
conn.commit()
conn.close()
print('Schema applied successfully!')
"
```

### التحقق من الجداول
```bash
python -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute(\"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename\")
for row in cur.fetchall():
    print('✅', row[0])
conn.close()
"
```

### الجداول الموجودة في قاعدة البيانات
| الجدول | الوصف |
|--------|-------|
| `roles` | أدوار المستخدمين |
| `branches` | بيانات الفروع |
| `users` | المستخدمون |
| `user_sessions` | سجل الدخول والخروج |
| `settings` | إعدادات النظام |
| `menu_categories` | فئات القائمة |
| `menu_items` | عناصر القائمة |
| `customers` | العملاء |
| `loyalty_accounts` | حسابات الولاء |
| `orders` | الطلبات |
| `order_items` | عناصر الطلبات |
| `sales_invoices` | فواتير المبيعات |
| `sales_invoice_items` | بنود فواتير المبيعات |
| `sales_returns` | مردود المبيعات |
| `sales_return_items` | بنود مردود المبيعات |
| `payments` | المدفوعات |
| `suppliers` | الموردون |
| `ingredients` | المكونات/المخزون |
| `inventory_transactions` | حركات المخزون |
| `kitchen_orders` | طلبات المطبخ |
| `kitchen_order_items` | عناصر طلبات المطبخ |
| `restaurant_tables` | طاولات المطعم |
| `reservations` | الحجوزات |
| `purchase_orders` | أوامر الشراء |
| `purchase_order_items` | عناصر أوامر الشراء |
| `audit_logs` | سجل التدقيق |

---

## 🖥️ إعداد SQL Server (لتطبيق Desktop - Windows فقط)

### المتطلبات
- Windows 10/11
- SQL Server 2019+ أو SQL Server Express
- Python 3.10+
- مكتبة `pymssql` (مثبتة — **لا تحتاج ODBC Driver**)

### تثبيت المكتبات
```bash
pip install pymssql bcrypt PyQt6
```

### إعداد متغيرات البيئة (Windows)
```cmd
set MSSQL_SERVER=localhost\SQLEXPRESS
set MSSQL_DATABASE=restaurant_management_system
set MSSQL_USER=sa
set MSSQL_PASSWORD=YourPassword
```

أو عبر PowerShell:
```powershell
$env:MSSQL_SERVER = "localhost\SQLEXPRESS"
$env:MSSQL_DATABASE = "restaurant_management_system"
$env:MSSQL_USER = "sa"
$env:MSSQL_PASSWORD = "YourPassword"
```

### إنشاء قاعدة البيانات في SQL Server (الطريقة الآلية)
```bash
python database/setup_mssql.py
```

### إنشاء قاعدة البيانات يدوياً في SQL Server Management Studio
```sql
-- تشغيل في SQL Server Management Studio
CREATE DATABASE restaurant_management_system;
GO

USE restaurant_management_system;
GO

-- ثم تشغيل محتوى ملف database/schema_mssql.sql
```

### تحويل المخطط لـ SQL Server
```bash
# تشغيل أداة التحويل
python -c "
import pymssql, os
conn = pymssql.connect(
    server=os.environ.get('MSSQL_SERVER', 'localhost'),
    database=os.environ.get('MSSQL_DATABASE', 'restaurant_management_system'),
    user=os.environ.get('MSSQL_USER', 'sa'),
    password=os.environ.get('MSSQL_PASSWORD', '')
)
print('✅ SQL Server connected successfully!')
conn.close()
"
```

### تشغيل تطبيق Desktop
```bash
python main.py
```

---

## 🔗 اتصال SQL Server بدون ODBC Driver

المشروع يستخدم **pymssql** بدلاً من pyodbc، مما يعني:
- ✅ **لا حاجة لتثبيت ODBC Driver 17/18 for SQL Server**
- ✅ يعمل مباشرة مع SQL Server عبر بروتوكول TDS
- ✅ يدعم Windows Authentication و SQL Authentication

```python
import pymssql

# SQL Authentication
conn = pymssql.connect(
    server='localhost\\SQLEXPRESS',
    database='restaurant_management_system',
    user='sa',
    password='your_password',
    charset='UTF-8'
)

# أو Windows Trusted Authentication
conn = pymssql.connect(
    server='localhost\\SQLEXPRESS',
    database='restaurant_management_system',
    trusted=True,
    charset='UTF-8'
)
```

---

## 🧪 اختبار النظام

### اختبار اتصال PostgreSQL
```bash
python -c "
import psycopg2, os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    count = cur.fetchone()[0]
    print(f'✅ PostgreSQL OK — عدد المستخدمين: {count}')
    conn.close()
except Exception as e:
    print(f'❌ خطأ: {e}')
"
```

### اختبار اتصال SQL Server
```bash
python -c "
import pymssql, os
try:
    conn = pymssql.connect(
        server=os.environ.get('MSSQL_SERVER', 'localhost'),
        database=os.environ.get('MSSQL_DATABASE', 'restaurant_management_system'),
        user=os.environ.get('MSSQL_USER', 'sa'),
        password=os.environ.get('MSSQL_PASSWORD', '')
    )
    print('✅ SQL Server OK')
    conn.close()
except Exception as e:
    print(f'❌ خطأ: {e}')
"
```

### اختبار تطبيق الويب
```bash
# تشغيل الخادم
python app.py &

# اختبار الوصول
curl -I http://localhost:5000/login
# يجب أن يعيد: HTTP/1.1 200 OK
```

### اختبار وحدات Python
```bash
python check.py
```

---

## 🌐 صفحات النظام

| الصفحة | المسار | الوصف |
|--------|--------|-------|
| تسجيل الدخول | `/login` | صفحة الدخول للنظام |
| لوحة التحكم | `/` | الإحصائيات والملخص |
| نقطة البيع | `/pos` | إدارة الطلبات والمبيعات |
| قائمة الطعام | `/menu` | إدارة القائمة والفئات |
| فواتير المبيعات | `/sales/invoices` | إنشاء وإدارة فواتير المبيعات |
| مردود المبيعات | `/sales/returns` | فواتير الإرجاع والمردود |
| الفروع | `/branches` | إدارة بيانات الفروع |
| المخزون | `/inventory` | إدارة المكونات والمخزون |
| الموردون | `/suppliers` | إدارة الموردين وأوامر الشراء |
| العملاء | `/customers` | إدارة العملاء ونقاط الولاء |
| المطبخ | `/kitchen` | نظام عرض المطبخ (KDS) |
| الحجوزات | `/reservations` | إدارة حجوزات الطاولات |
| التقارير | `/reports` | التقارير والإحصائيات |
| جلسات المستخدمين | `/sales/sessions` | سجل الدخول والخروج |
| الإعدادات | `/admin` | إعدادات النظام والمستخدمين |

---

## 🐛 حل المشاكل الشائعة

### خطأ: `DATABASE_URL not found`
```bash
# في Replit: قم بإنشاء قاعدة البيانات أولاً من لوحة التحكم
# أو تعيين المتغير يدوياً:
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
```

### خطأ: `pymssql connection failed`
```
1. تأكد من تشغيل خدمة SQL Server
2. تحقق من صحة MSSQL_SERVER و MSSQL_USER و MSSQL_PASSWORD
3. تأكد من تفعيل TCP/IP في SQL Server Configuration Manager
4. تأكد من أن SQL Server يقبل الاتصالات البعيدة
```

### خطأ: `port already in use`
```bash
# إيجاد العملية التي تستخدم المنفذ 5000
lsof -i :5000
# إيقاف العملية
kill -9 <PID>
```

### إعادة تعيين كلمة مرور المدير
```bash
python -c "
import bcrypt, psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
new_pass = 'admin123'
hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
cur.execute(\"UPDATE users SET password_hash=%s WHERE username='admin'\", (hashed,))
conn.commit()
conn.close()
print('✅ تم إعادة تعيين كلمة المرور إلى: admin123')
"
```

---

## 📊 هيكل المشروع

```
restaurant-management-system/
├── app.py                          # نقطة دخول الويب (Flask)
├── main.py                         # نقطة دخول Desktop (PyQt6)
├── requirements.txt                # المكتبات المطلوبة
├── SETUP_GUIDE.md                  # هذا الملف
│
├── database/
│   ├── connection.py               # اتصال SQL Server (pymssql)
│   ├── schema.sql                  # مخطط PostgreSQL
│   ├── schema_mssql.sql            # مخطط SQL Server / MSSQL
│   ├── setup_mssql.py              # أداة إنشاء قاعدة البيانات تلقائياً
│   └── __init__.py
│
├── services/                       # منطق الأعمال (Desktop)
│   ├── auth_service.py
│   ├── pos_service.py
│   ├── menu_service.py
│   └── ...
│
├── web/
│   ├── auth.py                     # المصادقة (PostgreSQL)
│   ├── db.py                       # اتصال PostgreSQL
│   ├── routes/
│   │   ├── auth_routes.py          # تسجيل الدخول/الخروج
│   │   ├── dashboard_routes.py     # لوحة التحكم
│   │   ├── pos_routes.py           # نقطة البيع
│   │   ├── sales_routes.py         # فواتير المبيعات والمردود ← جديد
│   │   ├── branches_routes.py      # إدارة الفروع ← جديد
│   │   ├── menu_routes.py
│   │   ├── inventory_routes.py
│   │   ├── kitchen_routes.py
│   │   ├── customers_routes.py
│   │   ├── reports_routes.py
│   │   ├── reservations_routes.py
│   │   ├── suppliers_routes.py
│   │   └── admin_routes.py
│   │
│   └── templates/
│       ├── base.html               # القالب الأساسي
│       ├── login.html
│       ├── dashboard.html
│       ├── pos.html
│       ├── sales_invoices.html     # فواتير المبيعات ← جديد
│       ├── sales_returns.html      # مردود المبيعات ← جديد
│       ├── branches.html           # الفروع ← جديد
│       ├── user_sessions.html      # جلسات المستخدمين ← جديد
│       └── ...
│
└── ui/                             # واجهات Desktop (PyQt6)
    ├── login_window.py
    ├── dashboard.py
    └── ...
```

---

## 📝 ملاحظات مهمة

1. **Replit** يعمل بـ **PostgreSQL** تلقائياً — تطبيق الويب (Flask) جاهز للتشغيل.
2. **تطبيق Desktop** (PyQt6 + SQL Server) يعمل على **Windows فقط** بسبب اعتماده على واجهة المستخدم الرسومية.
3. **pymssql** لا يتطلب تثبيت ODBC Driver — فقط تعريف متغيرات البيئة MSSQL_*.
4. كلمة المرور الافتراضية: `admin123` — **يُنصح بتغييرها فور تسجيل الدخول الأول**.

---

*إتقان سوفت للبرمجيات — Restaurant Management System v2.0*
