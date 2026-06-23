-- ====================================================================
-- نظام إدارة المطاعم - مخطط قاعدة البيانات (SQL Server / MSSQL)
-- itQAN Soft - Restaurant Management System
-- Requires: SQL Server 2019+ or SQL Server Express
-- ====================================================================

-- إنشاء قاعدة البيانات إذا لم تكن موجودة
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'restaurant_management_system')
BEGIN
    CREATE DATABASE restaurant_management_system;
END
GO

USE restaurant_management_system;
GO

-- ===================== جداول النظام =====================

-- الأدوار
IF OBJECT_ID(N'roles', N'U') IS NULL
BEGIN
    CREATE TABLE roles (
        role_id INT IDENTITY(1,1) PRIMARY KEY,
        role_name NVARCHAR(50) UNIQUE NOT NULL,
        description NVARCHAR(200) DEFAULT ''
    );
END
GO

-- الفروع (Branch Management)
IF OBJECT_ID(N'branches', N'U') IS NULL
BEGIN
    CREATE TABLE branches (
        branch_id INT IDENTITY(1,1) PRIMARY KEY,
        branch_code NVARCHAR(20) UNIQUE NOT NULL,
        arabic_name NVARCHAR(150) NOT NULL,
        foreign_name NVARCHAR(150) DEFAULT '',
        arabic_address NVARCHAR(MAX) DEFAULT '',
        foreign_address NVARCHAR(MAX) DEFAULT '',
        arabic_address2 NVARCHAR(MAX) DEFAULT '',
        foreign_address2 NVARCHAR(MAX) DEFAULT '',
        arabic_address3 NVARCHAR(MAX) DEFAULT '',
        foreign_address3 NVARCHAR(MAX) DEFAULT '',
        phone NVARCHAR(50) DEFAULT '',
        fax NVARCHAR(50) DEFAULT '',
        box_no NVARCHAR(50) DEFAULT '',
        email NVARCHAR(150) DEFAULT '',
        internet_location NVARCHAR(200) DEFAULT '',
        financial_year INT DEFAULT 1,
        is_main BIT DEFAULT 0,
        is_active BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- المستخدمون
IF OBJECT_ID(N'users', N'U') IS NULL
BEGIN
    CREATE TABLE users (
        user_id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(50) UNIQUE NOT NULL,
        full_name NVARCHAR(100) NOT NULL,
        email NVARCHAR(100) DEFAULT '',
        password_hash NVARCHAR(255) NOT NULL,
        role_id INT REFERENCES roles(role_id),
        branch_id INT REFERENCES branches(branch_id),
        is_active BIT DEFAULT 1,
        last_login DATETIME,
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- جلسات المستخدمين / سجل الدخول والخروج
IF OBJECT_ID(N'user_sessions', N'U') IS NULL
BEGIN
    CREATE TABLE user_sessions (
        session_id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT REFERENCES users(user_id),
        username NVARCHAR(50) NOT NULL,
        login_time DATETIME DEFAULT GETDATE(),
        logout_time DATETIME,
        machine_name NVARCHAR(100) DEFAULT '',
        ip_address NVARCHAR(50) DEFAULT '',
        branch_id INT REFERENCES branches(branch_id),
        session_status NVARCHAR(20) DEFAULT 'active'
    );
END
GO

-- الإعدادات
IF OBJECT_ID(N'settings', N'U') IS NULL
BEGIN
    CREATE TABLE settings (
        [key] NVARCHAR(100) PRIMARY KEY,
        [value] NVARCHAR(MAX) DEFAULT ''
    );
END
GO

-- فئات القائمة
IF OBJECT_ID(N'menu_categories', N'U') IS NULL
BEGIN
    CREATE TABLE menu_categories (
        category_id INT IDENTITY(1,1) PRIMARY KEY,
        category_name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX) DEFAULT '',
        sort_order INT DEFAULT 0,
        is_active BIT DEFAULT 1
    );
END
GO

-- عناصر القائمة
IF OBJECT_ID(N'menu_items', N'U') IS NULL
BEGIN
    CREATE TABLE menu_items (
        item_id INT IDENTITY(1,1) PRIMARY KEY,
        category_id INT REFERENCES menu_categories(category_id) ON DELETE CASCADE,
        item_name NVARCHAR(150) NOT NULL,
        description NVARCHAR(MAX) DEFAULT '',
        price NUMERIC(10,2) NOT NULL DEFAULT 0,
        cost_price NUMERIC(10,2) DEFAULT 0,
        is_available BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- العملاء
IF OBJECT_ID(N'customers', N'U') IS NULL
BEGIN
    CREATE TABLE customers (
        customer_id INT IDENTITY(1,1) PRIMARY KEY,
        full_name NVARCHAR(100) NOT NULL,
        phone NVARCHAR(30) DEFAULT '',
        email NVARCHAR(100) DEFAULT '',
        address NVARCHAR(MAX) DEFAULT '',
        notes NVARCHAR(MAX) DEFAULT '',
        date_of_birth DATE,
        is_active BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- حسابات الولاء
IF OBJECT_ID(N'loyalty_accounts', N'U') IS NULL
BEGIN
    CREATE TABLE loyalty_accounts (
        loyalty_id INT IDENTITY(1,1) PRIMARY KEY,
        customer_id INT UNIQUE REFERENCES customers(customer_id),
        points_balance INT DEFAULT 0,
        total_earned INT DEFAULT 0,
        total_redeemed INT DEFAULT 0,
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- حركات الولاء
IF OBJECT_ID(N'loyalty_transactions', N'U') IS NULL
BEGIN
    CREATE TABLE loyalty_transactions (
        lt_id INT IDENTITY(1,1) PRIMARY KEY,
        loyalty_id INT REFERENCES loyalty_accounts(loyalty_id),
        transaction_type NVARCHAR(30) NOT NULL,
        points INT NOT NULL,
        reference NVARCHAR(200) DEFAULT '',
        notes NVARCHAR(MAX) DEFAULT '',
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- الطلبات
IF OBJECT_ID(N'orders', N'U') IS NULL
BEGIN
    CREATE TABLE orders (
        order_id INT IDENTITY(1,1) PRIMARY KEY,
        customer_name NVARCHAR(100) DEFAULT N'زبون',
        customer_id INT REFERENCES customers(customer_id),
        served_by INT REFERENCES users(user_id),
        table_number NVARCHAR(20) DEFAULT '',
        branch_id INT REFERENCES branches(branch_id),
        subtotal NUMERIC(10,2) DEFAULT 0,
        discount_amount NUMERIC(10,2) DEFAULT 0,
        tax_amount NUMERIC(10,2) DEFAULT 0,
        total_amount NUMERIC(10,2) DEFAULT 0,
        payment_method NVARCHAR(50) DEFAULT N'Cash',
        payment_status NVARCHAR(30) DEFAULT N'Paid',
        order_status NVARCHAR(30) DEFAULT N'Completed',
        notes NVARCHAR(MAX) DEFAULT '',
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- عناصر الطلب
IF OBJECT_ID(N'order_items', N'U') IS NULL
BEGIN
    CREATE TABLE order_items (
        order_item_id INT IDENTITY(1,1) PRIMARY KEY,
        order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
        menu_item_id INT REFERENCES menu_items(item_id),
        item_name NVARCHAR(150) NOT NULL,
        quantity INT NOT NULL DEFAULT 1,
        unit_price NUMERIC(10,2) NOT NULL,
        subtotal NUMERIC(10,2) NOT NULL
    );
END
GO

-- فواتير المبيعات
IF OBJECT_ID(N'sales_invoices', N'U') IS NULL
BEGIN
    CREATE TABLE sales_invoices (
        invoice_id INT IDENTITY(1,1) PRIMARY KEY,
        invoice_no NVARCHAR(50) UNIQUE NOT NULL,
        invoice_date DATE NOT NULL DEFAULT GETDATE(),
        customer_id INT REFERENCES customers(customer_id),
        customer_name NVARCHAR(150) DEFAULT '',
        branch_id INT REFERENCES branches(branch_id),
        sales_rep_id INT REFERENCES users(user_id),
        payment_method NVARCHAR(50) DEFAULT N'نقدي',
        payment_type NVARCHAR(50) DEFAULT N'آجل',
        store_no NVARCHAR(20) DEFAULT '',
        center_no NVARCHAR(20) DEFAULT '',
        invoice_type NVARCHAR(30) DEFAULT N'فاتورة مبيعات',
        price_type NVARCHAR(30) DEFAULT N'سعر البيع',
        salesman_name NVARCHAR(100) DEFAULT '',
        salesman_commission NUMERIC(5,2) DEFAULT 0,
        subtotal NUMERIC(12,2) DEFAULT 0,
        discount_pct NUMERIC(5,2) DEFAULT 0,
        discount_amount NUMERIC(12,2) DEFAULT 0,
        tax_pct NUMERIC(5,2) DEFAULT 0,
        tax_amount NUMERIC(12,2) DEFAULT 0,
        total_amount NUMERIC(12,2) DEFAULT 0,
        paid_amount NUMERIC(12,2) DEFAULT 0,
        remaining_amount NUMERIC(12,2) DEFAULT 0,
        notes NVARCHAR(MAX) DEFAULT '',
        status NVARCHAR(30) DEFAULT N'مكتملة',
        created_by INT REFERENCES users(user_id),
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- بنود فواتير المبيعات
IF OBJECT_ID(N'sales_invoice_items', N'U') IS NULL
BEGIN
    CREATE TABLE sales_invoice_items (
        item_id INT IDENTITY(1,1) PRIMARY KEY,
        invoice_id INT REFERENCES sales_invoices(invoice_id) ON DELETE CASCADE,
        menu_item_id INT REFERENCES menu_items(item_id),
        item_name NVARCHAR(150) NOT NULL,
        item_code NVARCHAR(50) DEFAULT '',
        quantity NUMERIC(10,3) NOT NULL DEFAULT 1,
        unit NVARCHAR(30) DEFAULT '',
        unit_price NUMERIC(10,2) NOT NULL DEFAULT 0,
        discount_pct NUMERIC(5,2) DEFAULT 0,
        tax_pct NUMERIC(5,2) DEFAULT 0,
        subtotal NUMERIC(12,2) DEFAULT 0,
        notes NVARCHAR(MAX) DEFAULT ''
    );
END
GO

-- فواتير مردود المبيعات
IF OBJECT_ID(N'sales_returns', N'U') IS NULL
BEGIN
    CREATE TABLE sales_returns (
        return_id INT IDENTITY(1,1) PRIMARY KEY,
        return_no NVARCHAR(50) UNIQUE NOT NULL,
        return_date DATE NOT NULL DEFAULT GETDATE(),
        original_invoice_id INT REFERENCES sales_invoices(invoice_id),
        original_invoice_no NVARCHAR(50) DEFAULT '',
        customer_id INT REFERENCES customers(customer_id),
        customer_name NVARCHAR(150) DEFAULT '',
        branch_id INT REFERENCES branches(branch_id),
        store_no NVARCHAR(20) DEFAULT '',
        center_no NVARCHAR(20) DEFAULT '',
        payment_method NVARCHAR(50) DEFAULT N'نقدي',
        return_reason NVARCHAR(MAX) DEFAULT '',
        subtotal NUMERIC(12,2) DEFAULT 0,
        discount_amount NUMERIC(12,2) DEFAULT 0,
        tax_amount NUMERIC(12,2) DEFAULT 0,
        total_amount NUMERIC(12,2) DEFAULT 0,
        status NVARCHAR(30) DEFAULT N'معلقة',
        notes NVARCHAR(MAX) DEFAULT '',
        created_by INT REFERENCES users(user_id),
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- بنود مردود المبيعات
IF OBJECT_ID(N'sales_return_items', N'U') IS NULL
BEGIN
    CREATE TABLE sales_return_items (
        item_id INT IDENTITY(1,1) PRIMARY KEY,
        return_id INT REFERENCES sales_returns(return_id) ON DELETE CASCADE,
        menu_item_id INT REFERENCES menu_items(item_id),
        item_name NVARCHAR(150) NOT NULL,
        item_code NVARCHAR(50) DEFAULT '',
        quantity NUMERIC(10,3) NOT NULL DEFAULT 1,
        unit NVARCHAR(30) DEFAULT '',
        unit_price NUMERIC(10,2) DEFAULT 0,
        tax_pct NUMERIC(5,2) DEFAULT 0,
        quantity_invoiced NUMERIC(10,3) DEFAULT 0,
        discount_pct NUMERIC(5,2) DEFAULT 0,
        subtotal NUMERIC(12,2) DEFAULT 0
    );
END
GO

-- المدفوعات
IF OBJECT_ID(N'payments', N'U') IS NULL
BEGIN
    CREATE TABLE payments (
        payment_id INT IDENTITY(1,1) PRIMARY KEY,
        order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
        amount_paid NUMERIC(10,2) NOT NULL,
        payment_method NVARCHAR(50) DEFAULT N'Cash',
        reference_no NVARCHAR(100) DEFAULT '',
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- الموردون
IF OBJECT_ID(N'suppliers', N'U') IS NULL
BEGIN
    CREATE TABLE suppliers (
        supplier_id INT IDENTITY(1,1) PRIMARY KEY,
        supplier_name NVARCHAR(150) NOT NULL,
        contact_name NVARCHAR(100) DEFAULT '',
        phone NVARCHAR(30) DEFAULT '',
        email NVARCHAR(100) DEFAULT '',
        address NVARCHAR(MAX) DEFAULT '',
        is_active BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- المخزون
IF OBJECT_ID(N'ingredients', N'U') IS NULL
BEGIN
    CREATE TABLE ingredients (
        ingredient_id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(150) NOT NULL,
        unit NVARCHAR(30) DEFAULT N'كجم',
        current_stock NUMERIC(10,3) DEFAULT 0,
        minimum_stock NUMERIC(10,3) DEFAULT 0,
        reorder_level NUMERIC(10,3) DEFAULT 0,
        unit_cost NUMERIC(10,2) DEFAULT 0,
        supplier_id INT REFERENCES suppliers(supplier_id),
        is_active BIT DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- حركات المخزون
IF OBJECT_ID(N'inventory_transactions', N'U') IS NULL
BEGIN
    CREATE TABLE inventory_transactions (
        transaction_id INT IDENTITY(1,1) PRIMARY KEY,
        ingredient_id INT REFERENCES ingredients(ingredient_id),
        transaction_type NVARCHAR(30) NOT NULL,
        quantity NUMERIC(10,3) NOT NULL,
        unit_cost NUMERIC(10,2) DEFAULT 0,
        reference_no NVARCHAR(100) DEFAULT '',
        notes NVARCHAR(MAX) DEFAULT '',
        performed_by INT REFERENCES users(user_id),
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- طلبات المطبخ
IF OBJECT_ID(N'kitchen_orders', N'U') IS NULL
BEGIN
    CREATE TABLE kitchen_orders (
        kitchen_order_id INT IDENTITY(1,1) PRIMARY KEY,
        order_id INT REFERENCES orders(order_id),
        table_number NVARCHAR(20) DEFAULT '',
        customer_name NVARCHAR(100) DEFAULT '',
        status NVARCHAR(30) DEFAULT N'Pending',
        priority NVARCHAR(20) DEFAULT N'Normal',
        notes NVARCHAR(MAX) DEFAULT '',
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- عناصر طلبات المطبخ
IF OBJECT_ID(N'kitchen_order_items', N'U') IS NULL
BEGIN
    CREATE TABLE kitchen_order_items (
        kitchen_item_id INT IDENTITY(1,1) PRIMARY KEY,
        kitchen_order_id INT REFERENCES kitchen_orders(kitchen_order_id) ON DELETE CASCADE,
        item_name NVARCHAR(150) NOT NULL,
        quantity INT DEFAULT 1,
        notes NVARCHAR(MAX) DEFAULT '',
        status NVARCHAR(30) DEFAULT N'Pending'
    );
END
GO

-- طاولات المطعم
IF OBJECT_ID(N'restaurant_tables', N'U') IS NULL
BEGIN
    CREATE TABLE restaurant_tables (
        table_id INT IDENTITY(1,1) PRIMARY KEY,
        table_number NVARCHAR(20) NOT NULL,
        capacity INT DEFAULT 4,
        location NVARCHAR(100) DEFAULT N'القاعة الرئيسية',
        status NVARCHAR(20) DEFAULT N'Available',
        is_active BIT DEFAULT 1
    );
END
GO

-- جلسات الطاولات
IF OBJECT_ID(N'table_sessions', N'U') IS NULL
BEGIN
    CREATE TABLE table_sessions (
        session_id INT IDENTITY(1,1) PRIMARY KEY,
        table_id INT REFERENCES restaurant_tables(table_id),
        customer_name NVARCHAR(100) DEFAULT '',
        guests INT DEFAULT 1,
        status NVARCHAR(20) DEFAULT N'Open',
        opened_by INT REFERENCES users(user_id),
        opened_at DATETIME DEFAULT GETDATE(),
        closed_at DATETIME
    );
END
GO

-- الحجوزات
IF OBJECT_ID(N'reservations', N'U') IS NULL
BEGIN
    CREATE TABLE reservations (
        reservation_id INT IDENTITY(1,1) PRIMARY KEY,
        customer_name NVARCHAR(100) NOT NULL,
        phone NVARCHAR(30) DEFAULT '',
        table_id INT REFERENCES restaurant_tables(table_id),
        guests INT DEFAULT 1,
        reservation_date DATE NOT NULL,
        reservation_time TIME NOT NULL,
        status NVARCHAR(30) DEFAULT N'Confirmed',
        special_requests NVARCHAR(MAX) DEFAULT '',
        customer_id INT REFERENCES customers(customer_id),
        notes NVARCHAR(MAX) DEFAULT '',
        created_by INT REFERENCES users(user_id),
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- أوامر الشراء
IF OBJECT_ID(N'purchase_orders', N'U') IS NULL
BEGIN
    CREATE TABLE purchase_orders (
        po_id INT IDENTITY(1,1) PRIMARY KEY,
        supplier_id INT REFERENCES suppliers(supplier_id),
        created_by INT REFERENCES users(user_id),
        total_amount NUMERIC(10,2) DEFAULT 0,
        status NVARCHAR(30) DEFAULT N'Pending',
        expected_date DATE,
        received_date DATE,
        notes NVARCHAR(MAX) DEFAULT '',
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

-- عناصر أوامر الشراء
IF OBJECT_ID(N'purchase_order_items', N'U') IS NULL
BEGIN
    CREATE TABLE purchase_order_items (
        po_item_id INT IDENTITY(1,1) PRIMARY KEY,
        po_id INT REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
        ingredient_id INT REFERENCES ingredients(ingredient_id),
        quantity NUMERIC(10,3) NOT NULL,
        unit_cost NUMERIC(10,2) NOT NULL,
        subtotal NUMERIC(10,2) NOT NULL,
        received_qty NUMERIC(10,3) DEFAULT 0
    );
END
GO

-- سجل التدقيق
IF OBJECT_ID(N'audit_logs', N'U') IS NULL
BEGIN
    CREATE TABLE audit_logs (
        log_id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT REFERENCES users(user_id),
        action NVARCHAR(200) NOT NULL,
        table_name NVARCHAR(100) DEFAULT '',
        record_id INT,
        action_time DATETIME DEFAULT GETDATE()
    );
END
GO

-- ===================== البيانات الأولية =====================

-- أدوار المستخدمين
IF NOT EXISTS (SELECT 1 FROM roles WHERE role_name = 'Admin')
    INSERT INTO roles (role_name, description) VALUES ('Admin', 'مدير النظام');
IF NOT EXISTS (SELECT 1 FROM roles WHERE role_name = 'Manager')
    INSERT INTO roles (role_name, description) VALUES ('Manager', 'مدير الفرع');
IF NOT EXISTS (SELECT 1 FROM roles WHERE role_name = 'Cashier')
    INSERT INTO roles (role_name, description) VALUES ('Cashier', 'أمين الصندوق');
IF NOT EXISTS (SELECT 1 FROM roles WHERE role_name = 'Waiter')
    INSERT INTO roles (role_name, description) VALUES ('Waiter', 'نادل');
IF NOT EXISTS (SELECT 1 FROM roles WHERE role_name = 'Kitchen')
    INSERT INTO roles (role_name, description) VALUES ('Kitchen', 'مطبخ');
GO

-- الفرع الرئيسي
IF NOT EXISTS (SELECT 1 FROM branches WHERE branch_code = '001')
BEGIN
    INSERT INTO branches (branch_code, arabic_name, foreign_name, arabic_address, phone, email, financial_year, is_main, is_active)
    VALUES ('001', N'الفرع الرئيسي', N'Main Branch', N'المملكة العربية السعودية', '0500000000', 'main@restaurant.com', 1, 1, 1);
END
GO

-- المستخدم الافتراضي (admin / admin123)
DECLARE @admin_role_id INT = (SELECT role_id FROM roles WHERE role_name = 'Admin');
DECLARE @main_branch_id INT = (SELECT branch_id FROM branches WHERE branch_code = '001');

IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin') AND @admin_role_id IS NOT NULL AND @main_branch_id IS NOT NULL
BEGIN
    INSERT INTO users (username, full_name, email, password_hash, role_id, branch_id, is_active)
    VALUES ('admin', N'مدير النظام', 'admin@restaurant.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdCpWpFGC5NHIG2', @admin_role_id, @main_branch_id, 1);
END
GO

-- الإعدادات الأساسية
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'restaurant_name')
    INSERT INTO settings ([key], [value]) VALUES ('restaurant_name', N'مطعم إتقان');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'restaurant_address')
    INSERT INTO settings ([key], [value]) VALUES ('restaurant_address', N'المملكة العربية السعودية');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'restaurant_phone')
    INSERT INTO settings ([key], [value]) VALUES ('restaurant_phone', '0500000000');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'currency')
    INSERT INTO settings ([key], [value]) VALUES ('currency', N'ر.س');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'tax_rate')
    INSERT INTO settings ([key], [value]) VALUES ('tax_rate', '15');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'tax_enabled')
    INSERT INTO settings ([key], [value]) VALUES ('tax_enabled', '1');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'receipt_footer')
    INSERT INTO settings ([key], [value]) VALUES ('receipt_footer', N'شكراً لزيارتكم - نتمنى لكم تجربة ممتعة');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'loyalty_points_rate')
    INSERT INTO settings ([key], [value]) VALUES ('loyalty_points_rate', '1');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'loyalty_points_per_dollar')
    INSERT INTO settings ([key], [value]) VALUES ('loyalty_points_per_dollar', '1.0');
IF NOT EXISTS (SELECT 1 FROM settings WHERE [key] = 'primary_color')
    INSERT INTO settings ([key], [value]) VALUES ('primary_color', '#16a34a');
GO

PRINT '✅ SQL Server schema created successfully!';
PRINT '   Default login: admin / admin123';
GO
