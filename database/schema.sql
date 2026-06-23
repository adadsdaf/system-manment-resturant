-- ====================================================================
-- نظام إدارة المطاعم - مخطط قاعدة البيانات (PostgreSQL)
-- itQAN Soft - Restaurant Management System
-- ====================================================================

-- الأدوار
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- الفروع (Branch Management)
CREATE TABLE IF NOT EXISTS branches (
    branch_id SERIAL PRIMARY KEY,
    branch_code VARCHAR(20) UNIQUE NOT NULL,
    arabic_name VARCHAR(150) NOT NULL,
    foreign_name VARCHAR(150) DEFAULT '',
    arabic_address TEXT DEFAULT '',
    foreign_address TEXT DEFAULT '',
    arabic_address2 TEXT DEFAULT '',
    foreign_address2 TEXT DEFAULT '',
    arabic_address3 TEXT DEFAULT '',
    foreign_address3 TEXT DEFAULT '',
    phone VARCHAR(50) DEFAULT '',
    fax VARCHAR(50) DEFAULT '',
    box_no VARCHAR(50) DEFAULT '',
    email VARCHAR(150) DEFAULT '',
    internet_location VARCHAR(200) DEFAULT '',
    financial_year INTEGER DEFAULT 1,
    is_main BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- المستخدمون
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) DEFAULT '',
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(role_id),
    branch_id INTEGER REFERENCES branches(branch_id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جلسات المستخدمين / سجل الدخول والخروج
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    username VARCHAR(50) NOT NULL,
    login_time TIMESTAMP DEFAULT NOW(),
    logout_time TIMESTAMP,
    machine_name VARCHAR(100) DEFAULT '',
    ip_address VARCHAR(50) DEFAULT '',
    branch_id INTEGER REFERENCES branches(branch_id),
    session_status VARCHAR(20) DEFAULT 'active'
);

-- الإعدادات
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT DEFAULT ''
);

-- فئات القائمة
CREATE TABLE IF NOT EXISTS menu_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- عناصر القائمة
CREATE TABLE IF NOT EXISTS menu_items (
    item_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES menu_categories(category_id) ON DELETE CASCADE,
    item_name VARCHAR(150) NOT NULL,
    description TEXT DEFAULT '',
    price NUMERIC(10,2) NOT NULL DEFAULT 0,
    cost_price NUMERIC(10,2) DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- العملاء
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) DEFAULT '',
    email VARCHAR(100) DEFAULT '',
    address TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- حسابات الولاء
CREATE TABLE IF NOT EXISTS loyalty_accounts (
    customer_id INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    points_balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- الطلبات
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) DEFAULT 'زبون',
    customer_id INTEGER REFERENCES customers(customer_id),
    served_by INTEGER REFERENCES users(user_id),
    table_number VARCHAR(20) DEFAULT '',
    branch_id INTEGER REFERENCES branches(branch_id),
    subtotal NUMERIC(10,2) DEFAULT 0,
    discount_amount NUMERIC(10,2) DEFAULT 0,
    tax_amount NUMERIC(10,2) DEFAULT 0,
    total_amount NUMERIC(10,2) DEFAULT 0,
    payment_method VARCHAR(50) DEFAULT 'Cash',
    payment_status VARCHAR(30) DEFAULT 'Paid',
    order_status VARCHAR(30) DEFAULT 'Completed',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

-- عناصر الطلب
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(item_id),
    item_name VARCHAR(150) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL
);

-- فواتير المبيعات
CREATE TABLE IF NOT EXISTS sales_invoices (
    invoice_id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    customer_id INTEGER REFERENCES customers(customer_id),
    customer_name VARCHAR(150) DEFAULT '',
    branch_id INTEGER REFERENCES branches(branch_id),
    sales_rep_id INTEGER REFERENCES users(user_id),
    payment_method VARCHAR(50) DEFAULT 'نقدي',
    payment_type VARCHAR(50) DEFAULT 'آجل',
    store_no VARCHAR(20) DEFAULT '',
    center_no VARCHAR(20) DEFAULT '',
    invoice_type VARCHAR(30) DEFAULT 'فاتورة مبيعات',
    price_type VARCHAR(30) DEFAULT 'سعر البيع',
    salesman_name VARCHAR(100) DEFAULT '',
    salesman_commission NUMERIC(5,2) DEFAULT 0,
    subtotal NUMERIC(12,2) DEFAULT 0,
    discount_pct NUMERIC(5,2) DEFAULT 0,
    discount_amount NUMERIC(12,2) DEFAULT 0,
    tax_pct NUMERIC(5,2) DEFAULT 0,
    tax_amount NUMERIC(12,2) DEFAULT 0,
    total_amount NUMERIC(12,2) DEFAULT 0,
    paid_amount NUMERIC(12,2) DEFAULT 0,
    remaining_amount NUMERIC(12,2) DEFAULT 0,
    notes TEXT DEFAULT '',
    status VARCHAR(30) DEFAULT 'مكتملة',
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- بنود فواتير المبيعات
CREATE TABLE IF NOT EXISTS sales_invoice_items (
    item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES sales_invoices(invoice_id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(item_id),
    item_name VARCHAR(150) NOT NULL,
    item_code VARCHAR(50) DEFAULT '',
    quantity NUMERIC(10,3) NOT NULL DEFAULT 1,
    unit VARCHAR(30) DEFAULT '',
    unit_price NUMERIC(10,2) NOT NULL DEFAULT 0,
    discount_pct NUMERIC(5,2) DEFAULT 0,
    tax_pct NUMERIC(5,2) DEFAULT 0,
    subtotal NUMERIC(12,2) DEFAULT 0,
    notes TEXT DEFAULT ''
);

-- فواتير مردود المبيعات
CREATE TABLE IF NOT EXISTS sales_returns (
    return_id SERIAL PRIMARY KEY,
    return_no VARCHAR(50) UNIQUE NOT NULL,
    return_date DATE NOT NULL DEFAULT CURRENT_DATE,
    original_invoice_id INTEGER REFERENCES sales_invoices(invoice_id),
    original_invoice_no VARCHAR(50) DEFAULT '',
    customer_id INTEGER REFERENCES customers(customer_id),
    customer_name VARCHAR(150) DEFAULT '',
    branch_id INTEGER REFERENCES branches(branch_id),
    store_no VARCHAR(20) DEFAULT '',
    center_no VARCHAR(20) DEFAULT '',
    payment_method VARCHAR(50) DEFAULT 'نقدي',
    return_reason TEXT DEFAULT '',
    subtotal NUMERIC(12,2) DEFAULT 0,
    discount_amount NUMERIC(12,2) DEFAULT 0,
    tax_amount NUMERIC(12,2) DEFAULT 0,
    total_amount NUMERIC(12,2) DEFAULT 0,
    status VARCHAR(30) DEFAULT 'معلقة',
    notes TEXT DEFAULT '',
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- بنود مردود المبيعات
CREATE TABLE IF NOT EXISTS sales_return_items (
    item_id SERIAL PRIMARY KEY,
    return_id INTEGER REFERENCES sales_returns(return_id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(item_id),
    item_name VARCHAR(150) NOT NULL,
    item_code VARCHAR(50) DEFAULT '',
    quantity NUMERIC(10,3) NOT NULL DEFAULT 1,
    unit VARCHAR(30) DEFAULT '',
    unit_price NUMERIC(10,2) DEFAULT 0,
    tax_pct NUMERIC(5,2) DEFAULT 0,
    quantity_invoiced NUMERIC(10,3) DEFAULT 0,
    discount_pct NUMERIC(5,2) DEFAULT 0,
    subtotal NUMERIC(12,2) DEFAULT 0
);

-- المدفوعات
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    amount_paid NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Cash',
    reference_no VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

-- الموردون
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(100) DEFAULT '',
    phone VARCHAR(30) DEFAULT '',
    email VARCHAR(100) DEFAULT '',
    address TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- المخزون
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    unit VARCHAR(30) DEFAULT 'كجم',
    current_stock NUMERIC(10,3) DEFAULT 0,
    minimum_stock NUMERIC(10,3) DEFAULT 0,
    reorder_level NUMERIC(10,3) DEFAULT 0,
    unit_cost NUMERIC(10,2) DEFAULT 0,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- حركات المخزون
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id SERIAL PRIMARY KEY,
    ingredient_id INTEGER REFERENCES ingredients(ingredient_id),
    transaction_type VARCHAR(30) NOT NULL,
    quantity NUMERIC(10,3) NOT NULL,
    unit_cost NUMERIC(10,2) DEFAULT 0,
    reference_no VARCHAR(100) DEFAULT '',
    notes TEXT DEFAULT '',
    performed_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- طلبات المطبخ
CREATE TABLE IF NOT EXISTS kitchen_orders (
    kitchen_order_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    table_number VARCHAR(20) DEFAULT '',
    customer_name VARCHAR(100) DEFAULT '',
    status VARCHAR(30) DEFAULT 'Pending',
    priority VARCHAR(20) DEFAULT 'Normal',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- عناصر طلبات المطبخ
CREATE TABLE IF NOT EXISTS kitchen_order_items (
    id SERIAL PRIMARY KEY,
    kitchen_order_id INTEGER REFERENCES kitchen_orders(kitchen_order_id) ON DELETE CASCADE,
    item_name VARCHAR(150) NOT NULL,
    quantity INTEGER DEFAULT 1,
    status VARCHAR(30) DEFAULT 'Pending'
);

-- طاولات المطعم
CREATE TABLE IF NOT EXISTS restaurant_tables (
    table_id SERIAL PRIMARY KEY,
    table_number VARCHAR(20) NOT NULL,
    capacity INTEGER DEFAULT 4,
    location VARCHAR(100) DEFAULT 'القاعة الرئيسية',
    is_active BOOLEAN DEFAULT TRUE
);

-- الحجوزات
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) DEFAULT '',
    table_id INTEGER REFERENCES restaurant_tables(table_id),
    guests INTEGER DEFAULT 1,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    status VARCHAR(30) DEFAULT 'Confirmed',
    special_requests TEXT DEFAULT '',
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- أوامر الشراء
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    created_by INTEGER REFERENCES users(user_id),
    total_amount NUMERIC(10,2) DEFAULT 0,
    status VARCHAR(30) DEFAULT 'Pending',
    expected_date DATE,
    received_date DATE,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

-- عناصر أوامر الشراء
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(ingredient_id),
    quantity NUMERIC(10,3) NOT NULL,
    unit_cost NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL
);

-- سجل التدقيق
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(200) NOT NULL,
    table_name VARCHAR(100) DEFAULT '',
    record_id INTEGER,
    action_time TIMESTAMP DEFAULT NOW()
);

-- ─── نظام التراخيص ─────────────────────────────────────────────

-- إعدادات الترخيص
CREATE TABLE IF NOT EXISTS license_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL DEFAULT '',
    description TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- الأجهزة المرخصة
CREATE TABLE IF NOT EXISTS licensed_devices (
    device_id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    machine_fingerprint VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50) DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    added_by INTEGER REFERENCES users(user_id),
    added_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    notes TEXT DEFAULT ''
);

-- سجل عمليات الترخيص
CREATE TABLE IF NOT EXISTS license_audit_log (
    log_id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    device_name VARCHAR(100) DEFAULT '',
    machine_fingerprint VARCHAR(255) DEFAULT '',
    performed_by INTEGER REFERENCES users(user_id),
    ip_address VARCHAR(50) DEFAULT '',
    details TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===================== البيانات الأولية =====================

INSERT INTO roles (role_name) VALUES ('Admin'), ('Manager'), ('Cashier'), ('Waiter'), ('Kitchen'), ('Owner')
ON CONFLICT DO NOTHING;

INSERT INTO branches (branch_code, arabic_name, foreign_name, arabic_address, phone, email, financial_year, is_main, is_active)
VALUES ('001', 'الفرع الرئيسي', 'Main Branch', 'المملكة العربية السعودية', '0500000000', 'main@restaurant.com', 1, TRUE, TRUE)
ON CONFLICT DO NOTHING;

-- كلمة المرور الافتراضية: admin123
INSERT INTO users (username, full_name, email, password_hash, role_id, branch_id, is_active)
VALUES (
    'admin', 'مدير النظام', 'admin@restaurant.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdCpWpFGC5NHIG2', 1, 1, TRUE
) ON CONFLICT (username) DO NOTHING;

INSERT INTO settings (key, value) VALUES
    ('restaurant_name', 'مطعم إتقان'),
    ('restaurant_address', 'المملكة العربية السعودية'),
    ('restaurant_phone', '0500000000'),
    ('currency', 'ر.س'),
    ('tax_rate', '15'),
    ('tax_enabled', '1'),
    ('receipt_footer', 'شكراً لزيارتكم - نتمنى لكم تجربة ممتعة'),
    ('loyalty_points_rate', '1')
ON CONFLICT (key) DO NOTHING;
