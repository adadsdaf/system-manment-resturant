# دليل نظام إدارة المطاعم - Restaurant Management System

---

## 1. نظرة عامة على النظام

نظام إدارة المطاعم هو تطبيق متكامل مصمم لإدارة جميع عمليات المطعم من نقطة بيع واحدة. يتألف النظام من واجهتين:

- **تطبيق سطح المكتب (Desktop App)** — مبني بـ PyQt6 للاستخدام المحلي
- **تطبيق الويب (Web App)** — مبني بـ Flask للوصول عبر المتصفح

---

## 2. المتطلبات الأساسية

### للتطبيق Desktop
```
- Windows 10/11
- Python 3.10 أو أحدث
- SQL Server (أو SQL Server Express)
- ODBC Driver 17 for SQL Server
```

### لتطبيق الويب
```
- Python 3.10 أو أحدث
- PostgreSQL 12 أو أحدث
- pip
```

### المكتبات المطلوبة
```
PyQt6>=6.5.0
pyodbc>=4.0.0
bcrypt>=4.0.0
flask>=3.0.0
psycopg2-binary>=2.9.0
Werkzeug>=3.0.0
```

---

## 3. هيكل المشروع

```
restaurant-management-system/
├── main.py                    # نقطة دخول التطبيق Desktop
├── app.py                     # نقطة دخول تطبيق الويب (Flask)
├── requirements.txt           # قائمة المكتبات المطلوبة
│
├── database/
│   ├── __init__.py
│   └── connection.py          # إعداد اتصال SQL Server
│
├── services/                  # طبقة الخدمات (Backend Logic)
│   ├── auth_service.py        # تسجيل الدخول، كلمات المرور، سجل العمليات
│   ├── admin_service.py       # إدارة المستخدمين، الإعدادات، النسخ الاحتياطي
│   ├── pos_service.py         # نقطة البيع، الطلبات، برنامج الولاء
│   ├── menu_service.py        # إدارة القائمة والإحصائيات
│   ├── inventory_service.py   # إدارة المخزون والحركات
│   ├── supplier_service.py    # إدارة الموردين وأوامر الشراء
│   ├── customer_service.py    # إدارة العملاء ونقاط الولاء
│   ├── kitchen_service.py     # نظام عرض المطبخ (KDS)
│   ├── reservation_service.py # إدارة الحجوزات
│   ├── reports_service.py     # التقارير والتحليلات
│   └── table_service.py       # إدارة الطاولات
│
├── ui/                        # واجهات المستخدم Desktop
│   ├── login_window.py        # نافذة تسجيل الدخول
│   ├── dashboard.py           # لوحة التحكم الرئيسية
│   ├── pos.py                 # واجهة نقطة البيع
│   ├── menu_management.py     # إدارة عناصر القائمة
│   ├── table_management.py    # إدارة الطاولات
│   ├── kitchen.py             # عرض المطبخ
│   ├── inventory.py           # إدارة المخزون
│   ├── suppliers.py           # إدارة الموردين
│   ├── customers.py           # إدارة العملاء
│   ├── reservations.py        # إدارة الحجوزات
│   ├── reports.py             # التقارير والتحليلات
│   └── admin_settings.py      # الإعدادات وإدارة المستخدمين
│
├── assets/
│   ├── __init__.py
│   └── styles.py              # الأنماط والألوان المشتركة
│
└── web/                       # تطبيق الويب
    ├── db.py                  # اتصال PostgreSQL
    ├── auth.py                # مصادقة الويب
    └── routes/
        ├── auth_routes.py
        ├── dashboard_routes.py
        ├── pos_routes.py
        ├── menu_routes.py
        ├── inventory_routes.py
        ├── kitchen_routes.py
        ├── customers_routes.py
        ├── reports_routes.py
        ├── reservations_routes.py
        ├── suppliers_routes.py
        └── admin_routes.py
```

---

## 4. هيكل قاعدة البيانات

### الجداول الرئيسية:

| اسم الجدول | الوصف |
|-----------|--------|
| `users` | مستخدمي النظام (موظفين، مديرين) |
| `roles` | أدوار المستخدمين |
| `settings` | إعدادات النظام |
| `menu_categories` | تصنيفات القائمة |
| `menu_items` | عناصر القائمة |
| `orders` | الطلبات |
| `order_items` | تفاصيل الطلبات |
| `payments` | المدفوعات |
| `customers` | العملاء |
| `loyalty_accounts` | حسابات برنامج الولاء |
| `loyalty_transactions` | حركات نقاط الولاء |
| `restaurant_tables` | طاولات المطعم |
| `table_sessions` | جلسات الطاولات |
| `reservations` | الحجوزات |
| `ingredients` | المكونات والمخزون |
| `inventory_transactions` | حركات المخزون |
| `suppliers` | الموردين |
| `purchase_orders` | أوامر الشراء |
| `purchase_order_items` | تفاصيل أوامر الشراء |
| `kitchen_orders` | طلبات المطبخ |
| `kitchen_order_items` | تفاصيل طلبات المطبخ |
| `audit_logs` | سجل العمليات |

---

## 5. كيفية التثبيت والتشغيل

### تشغيل تطبيق سطح المكتب

**الخطوة 1 — تثبيت Python**
تأكد من وجود Python 3.10+ مثبت على النظام.

**الخطوة 2 — تثبيت SQL Server**
ثبت SQL Server Express أو الإصدار الكامل، وتأكد من تفعيل "Windows Authentication".

**الخطوة 3 — تثبيت ODBC Driver**
ثبت [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

**الخطوة 4 — إنشاء قاعدة البيانات**
افتح SQL Server Management Studio (SSMS) ونفذ الاستعلامات التالية لإنشاء قاعدة البيانات والجداول:

```sql
CREATE DATABASE restaurant_management_system;
GO

USE restaurant_management_system;
GO

-- جدول الأدوار
CREATE TABLE roles (
    role_id INT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(50) UNIQUE NOT NULL,
    description NVARCHAR(255)
);
INSERT INTO roles (role_name, description) VALUES
('Admin', 'Administrator with full access'),
('Manager', 'Manager with most access'),
('Cashier', 'POS operator'),
('Waiter', 'Waitstaff with limited access'),
('Kitchen', 'Kitchen staff');

-- جدول المستخدمين
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    full_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100),
    password_hash NVARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1,
    last_login DATETIME,
    role_id INT FOREIGN KEY REFERENCES roles(role_id),
    created_at DATETIME DEFAULT GETDATE()
);
-- المستخدم الافتراضي: admin / admin123

-- جدول الإعدادات
CREATE TABLE settings (
    [key] NVARCHAR(100) PRIMARY KEY,
    [value] NVARCHAR(500)
);
INSERT INTO settings ([key], [value]) VALUES
('restaurant_name', 'RestaurantPro'),
('restaurant_address', ''),
('restaurant_phone', ''),
('currency', '$'),
('tax_rate', '16'),
('tax_enabled', '1'),
('loyalty_points_per_dollar', '1'),
('receipt_footer', 'Thank you for dining with us!'),
('primary_color', '#16a34a');

-- جدول تصنيفات القائمة
CREATE TABLE menu_categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(50) UNIQUE NOT NULL,
    description NVARCHAR(255),
    is_active BIT DEFAULT 1
);
INSERT INTO menu_categories (category_name, description, is_active) VALUES
('Main Course', 'Main dishes', 1),
('Beverages', 'Drinks and juices', 1),
('Desserts', 'Sweet dishes', 1),
('Appetizers', 'Starters', 1);

-- جدول عناصر القائمة
CREATE TABLE menu_items (
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    category_id INT FOREIGN KEY REFERENCES menu_categories(category_id),
    item_name NVARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    description NVARCHAR(255),
    is_available BIT DEFAULT 1,
    updated_at DATETIME DEFAULT GETDATE()
);

-- جدول الطلبات
CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_name NVARCHAR(100) DEFAULT 'Guest',
    customer_id INT NULL,
    served_by INT FOREIGN KEY REFERENCES users(user_id),
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method NVARCHAR(20) NOT NULL,
    payment_status NVARCHAR(20) DEFAULT 'Paid',
    order_status NVARCHAR(20) DEFAULT 'Completed',
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول تفاصيل الطلبات
CREATE TABLE order_items (
    order_item_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    menu_item_id INT NULL,
    item_name NVARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- جدول المدفوعات
CREATE TABLE payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method NVARCHAR(20) NOT NULL,
    reference_no NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول المكونات (المخزون)
CREATE TABLE ingredients (
    ingredient_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) UNIQUE NOT NULL,
    unit NVARCHAR(20) NOT NULL,
    current_stock DECIMAL(10,2) DEFAULT 0,
    minimum_stock DECIMAL(10,2) DEFAULT 0,
    reorder_level DECIMAL(10,2) DEFAULT 0,
    unit_cost DECIMAL(10,2) DEFAULT 0,
    supplier_id INT NULL,
    is_active BIT DEFAULT 1,
    updated_at DATETIME DEFAULT GETDATE()
);

-- جدول حركات المخزون
CREATE TABLE inventory_transactions (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    ingredient_id INT FOREIGN KEY REFERENCES ingredients(ingredient_id),
    transaction_type NVARCHAR(20) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2),
    reference_no NVARCHAR(100),
    notes NVARCHAR(255),
    performed_by INT FOREIGN KEY REFERENCES users(user_id),
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول الموردين
CREATE TABLE suppliers (
    supplier_id INT IDENTITY(1,1) PRIMARY KEY,
    supplier_name NVARCHAR(100) UNIQUE NOT NULL,
    contact_name NVARCHAR(100),
    phone NVARCHAR(20),
    email NVARCHAR(100),
    address NVARCHAR(255),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول أوامر الشراء
CREATE TABLE purchase_orders (
    po_id INT IDENTITY(1,1) PRIMARY KEY,
    supplier_id INT FOREIGN KEY REFERENCES suppliers(supplier_id),
    created_by INT FOREIGN KEY REFERENCES users(user_id),
    total_amount DECIMAL(10,2) NOT NULL,
    notes NVARCHAR(255),
    expected_date DATE,
    received_date DATETIME,
    status NVARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول تفاصيل أوامر الشراء
CREATE TABLE purchase_order_items (
    po_item_id INT IDENTITY(1,1) PRIMARY KEY,
    po_id INT FOREIGN KEY REFERENCES purchase_orders(po_id),
    ingredient_id INT FOREIGN KEY REFERENCES ingredients(ingredient_id),
    quantity DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    received_qty DECIMAL(10,2) DEFAULT 0
);

-- جدول العملاء
CREATE TABLE customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(100) NOT NULL,
    phone NVARCHAR(20) UNIQUE,
    email NVARCHAR(100),
    address NVARCHAR(255),
    date_of_birth DATE,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول حسابات الولاء
CREATE TABLE loyalty_accounts (
    loyalty_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT FOREIGN KEY REFERENCES customers(customer_id),
    points_balance INT DEFAULT 0,
    total_earned INT DEFAULT 0,
    total_redeemed INT DEFAULT 0
);

-- جدول حركات الولاء
CREATE TABLE loyalty_transactions (
    lt_id INT IDENTITY(1,1) PRIMARY KEY,
    loyalty_id INT FOREIGN KEY REFERENCES loyalty_accounts(loyalty_id),
    transaction_type NVARCHAR(20) NOT NULL,
    points INT NOT NULL,
    reference NVARCHAR(100),
    notes NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE()
);

-- جدول الطاولات
CREATE TABLE restaurant_tables (
    table_id INT IDENTITY(1,1) PRIMARY KEY,
    table_number NVARCHAR(10) UNIQUE NOT NULL,
    capacity INT NOT NULL,
    location NVARCHAR(50),
    status NVARCHAR(20) DEFAULT 'Available',
    is_active BIT DEFAULT 1
);

-- جدول جلسات الطاولات
CREATE TABLE table_sessions (
    session_id INT IDENTITY(1,1) PRIMARY KEY,
    table_id INT FOREIGN KEY REFERENCES restaurant_tables(table_id),
    customer_name NVARCHAR(100),
    guests INT DEFAULT 1,
    opened_by INT FOREIGN KEY REFERENCES users(user_id),
    status NVARCHAR(20) DEFAULT 'Open',
    opened_at DATETIME DEFAULT GETDATE(),
    closed_at DATETIME
);

-- جدول الحجوزات
CREATE TABLE reservations (
    reservation_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_name NVARCHAR(100) NOT NULL,
    phone NVARCHAR(20),
    customer_id INT NULL,
    table_id INT FOREIGN KEY REFERENCES restaurant_tables(table_id),
    guests INT NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time NVARCHAR(10) NOT NULL,
    special_requests NVARCHAR(255),
    status NVARCHAR(20) DEFAULT 'Pending',
    created_by INT FOREIGN KEY REFERENCES users(user_id),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- جدول طلبات المطبخ
CREATE TABLE kitchen_orders (
    kitchen_order_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    table_number NVARCHAR(10),
    customer_name NVARCHAR(100),
    notes NVARCHAR(255),
    status NVARCHAR(20) DEFAULT 'Pending',
    priority NVARCHAR(10) DEFAULT 'Normal',
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- جدول تفاصيل طلبات المطبخ
CREATE TABLE kitchen_order_items (
    kitchen_item_id INT IDENTITY(1,1) PRIMARY KEY,
    kitchen_order_id INT FOREIGN KEY REFERENCES kitchen_orders(kitchen_order_id),
    item_name NVARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    notes NVARCHAR(255),
    status NVARCHAR(20) DEFAULT 'Pending'
);

-- جدول سجل العمليات
CREATE TABLE audit_logs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES users(user_id),
    action NVARCHAR(100) NOT NULL,
    table_name NVARCHAR(50),
    record_id INT,
    action_time DATETIME DEFAULT GETDATE()
);
GO
```

**الخطوة 5 — تثبيت المكتبات**
```bash
pip install -r requirements.txt
pip install pyodbc
```

**الخطوة 6 — تشغيل التطبيق**
```bash
python main.py
```

---

### تشغيل تطبيق الويب

**الخطوة 1 — تثبيت PostgreSQL**
ثبت PostgreSQL 12+ وأنشئ قاعدة البيانات.

**الخطوة 2 — إنشاء قاعدة البيانات**
```sql
CREATE DATABASE restaurant_management_system;
```

**الخطوة 3 — إنشاء الجداول**
نفس الجداول المذكورة أعلاه مع تعديل بسيط لأنواع البيانات لتتناسب مع PostgreSQL (استبدال `IDENTITY(1,1)` بـ `SERIAL PRIMARY KEY`، `NVARCHAR` بـ `VARCHAR`، `BIT` بـ `BOOLEAN`، `DATETIME` بـ `TIMESTAMP`، `DECIMAL` بـ `NUMERIC`).

**الخطوة 4 — تثبيت المكتبات**
```bash
pip install -r requirements.txt
```

**الخطوة 5 — تشغيل التطبيق**
```bash
python app.py
```
التطبيق يعمل على `http://localhost:5000`

---

## 6. المستخدم الافتراضي

| الحقل | القيمة |
|--------|--------|
| اسم المستخدم | `admin` |
| كلمة المرور | `admin123` |
| الدور | Admin |

> ملاحظة: عند أول تشغيل، يقوم النظام بتشفير كلمة مرور admin تلقائياً باستخدام bcrypt.

---

## 7. الميزات المتوفرة

### 7.1 لوحة التحكم (Dashboard)
- ملخص المبيعات اليومية
- عدد الطلبات اليوم
- عدد عناصر القائمة النشطة
- إحصائيات سريعة

### 7.2 إدارة القائمة (Menu Management)
- إضافة/تعديل/حذف عناصر القائمة
- إنشاء تصنيفات مخصصة
- تفعيل/تعطيل العناصر
- تصدير إلى CSV
- طباعة القائمة

### 7.3 نقطة البيع (POS)
- تصفح القائمة حسب التصنيف
- البحث عن العناصر
- إضافة عناصر إلى السلة
- تعديل الكميات
- خصومات
- حساب تلقائي للضريبة
- طرق دفع: نقدي، MPESA، بطاقة
- ربط العملاء بالسلة
- طباعة الإيصال

### 7.4 إدارة الطاولات (Table Manager)
- عرض جميع الطاولات
- فتح/إغلاق جلسة الطاولة
- حجز الطاولات
- نقل العملاء بين طاولات
- فلتر حسب الموقع
- إضافة/تعديل/حذف طاولات

### 7.5 عرض المطبخ (Kitchen Display)
- عرض طلبات المطبخ بالوقت الفعلي
- تحديث حالة الطلب (قيد التحضير، جاهز، تم التقديم)
- تغيير الأولوية (عادي / عاجل)
- مؤقت لكل طلب
- فلتر حسب الحالة
- تحديث تلقائي كل 15 ثانية

### 7.6 إدارة المخزون (Inventory)
- إضافة/تعديل/حذف المكونات
- دخول مخزون (Stock In)
- خروج مخزون (Stock Out)
- تعديل يدوي للمخزون
- تتبع حركات المخزون
- تنبيهات انخفاض المخزون

### 7.7 إدارة الموردين (Suppliers)
- إضافة/تعديل/حذف الموردين
- إنشاء أوامر شراء
- إضافة عناصر لأمر الشراء
- استلام أوامر الشراء
- إلغاء أوامر الشراء
- عرض تفاصيل أمر الشراء

### 7.8 إدارة العملاء (Customers)
- إضافة/تعديل/حذف العملاء
- عرض سجل طلبات العميل
- إدارة نقاط الولاء
- استبدال النقاط
- إضافة نقاط يدوياً
- تنبيه أعياد الميلاد

### 7.9 إدارة الحجوزات (Reservations)
- إنشاء/تعديل/حذف حجوزات
- بحث عن عميل عبر الهاتف
- ربط الحجز بطاولة
- تغيير حالة الحجز
- فلتر حسب التاريخ والحالة

### 7.10 التقارير (Reports)
- ملخص المبيعات (اليوم/الأسبوع/الشهر)
- المبيعات اليومية
- المبيعات حسب طريقة الدفع
- أفضل العناصر مبيعاً
- المبيعات حسب التصنيف
- أفضل العملاء
- أداء الموظفين
- تنبيهات المخزون المنخفض
- المبيعات حسب الساعة
- تصدير إلى CSV

### 7.11 الإعدادات والإدارة (Admin Settings)
- إدارة المستخدمين (إضافة/تعديل/قفل/فتح)
- إعادة تعيين كلمات المرور
- إعدادات المطعم (الاسم، العنوان، الهاتف)
- الإعدادات المالية (العملة، الضريبة)
- إعدادات برنامج الولاء
- تخصيص الألوان والشعار
- سجل العمليات (Audit Logs)
- نسخ احتياطي لقاعدة البيانات
- تصدير البيانات إلى CSV

---

## 8. الأدوار والصلاحيات

| الدور | الوصف |
|--------|-------|
| **Admin** | صلاحيات كاملة على جميع الميزات |
| **Manager** | صلاحيات واسعة مع قيود بسيطة |
| **Cashier** | تشغيل نقطة البيع فقط |
| **Waiter** | عرض وتحديث حالة الطاولات |
| **Kitchen** | عرض وتحديث طلبات المطبخ |

---

## 9. استكشاف الأخطاء الشائعة

### خطأ الاتصال بقاعدة البيانات
تأكد من:
- تشغيل SQL Server
- صحة اسم الخادم في `database/connection.py`
- تفعيل "Windows Authentication"

### خطأ في تثبيت pyodbc
```
pip install pyodbc --only-binary=:all:
```

### خطأ في مكتبات الويب
```bash
pip install psycopg2-binary flask werkzeug bcrypt
```

### قاعدة البيانات فارغة
بعد إنشاء قاعدة البيانات وتشغيل التطبيق، سجل الدخول بـ `admin/admin123` ثم انتقل إلى Settings لإضافة البيانات الأولية.

---

## 10. ملاحظات التطوير

- المشروع مفتوح المصدر تحت رخصة MIT
- الإصدار الحالي: v1.0
- يحتوي على تطبيقين منفصلين (Desktop + Web) يمكن تشغيلهما بشكل مستقل
- خدمة `development_log.md` فارغة ويمكن استخدامها لتسجيل تقدم التطوير
- يحتوي المشروع على سجل مبيعات تجريبي في ملف `sales_report_month.csv`

---

## 11. آلية العمل

```
┌─────────────────────────────────────────────────────┐
│                    المستخدم                          │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐           ┌────▼────┐
   │ Desktop │           │  Web   │
   │  App   │           │  App   │
   │PyQt6   │           │ Flask  │
   └────┬────┘           └────┬────┘
        │                     │
        │    ┌────────────────┘
        │    │
   ┌────▼────▼────┐
   │   Services    │
   │  (Business    │
   │   Logic)      │
   └────┬──────────┘
        │
   ┌────▼────────────┐
   │   Database      │
   │  (SQL Server /  │
   │   PostgreSQL)   │
   └─────────────────┘
```

---

*تم إنشاء هذا الدليل بتاريخ: 2026-06-23*
