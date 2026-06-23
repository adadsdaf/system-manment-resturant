-- نظام إدارة المطاعم - مخطط قاعدة البيانات
-- itQAN Soft - Restaurant Management System

-- الأدوار
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- المستخدمون
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) DEFAULT '',
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
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

-- المخزون - المكونات
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

-- ===================== البيانات الأولية =====================

INSERT INTO roles (role_name) VALUES ('Admin'), ('Manager'), ('Cashier')
ON CONFLICT DO NOTHING;

-- كلمة المرور الافتراضية: admin123
INSERT INTO users (username, full_name, email, password_hash, role_id, is_active)
VALUES (
    'admin',
    'مدير النظام',
    'admin@restaurant.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdCpWpFGC5NHIG2',
    1,
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- الإعدادات الافتراضية
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

-- فئات القائمة
INSERT INTO menu_categories (category_name, description, sort_order) VALUES
    ('فطائر الدجاج واللحوم', 'فطائر شهية بالدجاج واللحوم', 1),
    ('فطائر الحلو', 'فطائر بالمربى والعسل', 2),
    ('فطر مشكلت', 'أطباق الفطر المتنوعة', 3),
    ('المكرونة', 'أطباق المكرونة المتنوعة', 4),
    ('الأرز', 'أطباق الأرز', 5),
    ('المشروبات', 'مشروبات ساخنة وباردة', 6),
    ('الحلويات', 'حلويات متنوعة', 7)
ON CONFLICT DO NOTHING;

-- عناصر القائمة
INSERT INTO menu_items (category_id, item_name, description, price, cost_price, is_available) VALUES
    (1, 'كريسبي دجاج', 'دجاج مقرمش بالتوابل', 40, 18, TRUE),
    (1, 'تشيكن رول وسط حار', 'رول دجاج حار متوسط', 20, 8, TRUE),
    (1, 'تشيكن رول وسط عادي', 'رول دجاج عادي متوسط', 52, 20, TRUE),
    (1, 'هيكس دجاج', 'مزيج دجاج مميز', 87, 35, TRUE),
    (2, 'فطيرة عسل', 'فطيرة بالعسل الطبيعي', 25, 10, TRUE),
    (2, 'فطيرة نوتيلا', 'فطيرة بكريمة النوتيلا', 30, 12, TRUE),
    (3, 'فطر مشوي', 'فطر مشوي بالثوم', 35, 14, TRUE),
    (3, 'فطر بالكريمة', 'فطر بصوص الكريمة', 40, 16, TRUE),
    (4, 'مكرونة بشاميل', 'مكرونة بصوص البشاميل', 35, 12, TRUE),
    (4, 'مكرونة بولونيز', 'مكرونة باللحم المفروم', 45, 18, TRUE),
    (5, 'أرز بالدجاج', 'أرز مع دجاج مشوي', 30, 12, TRUE),
    (5, 'أرز مندي', 'أرز مندي على الحطب', 55, 22, TRUE),
    (6, 'قهوة عربية', 'قهوة عربية أصيلة', 15, 3, TRUE),
    (6, 'شاي بالنعناع', 'شاي طازج بالنعناع', 10, 2, TRUE),
    (6, 'عصير برتقال', 'عصير برتقال طازج', 20, 5, TRUE),
    (7, 'كنافة', 'كنافة بالجبن', 25, 8, TRUE),
    (7, 'أم علي', 'حلوى أم علي التقليدية', 20, 7, TRUE)
ON CONFLICT DO NOTHING;

-- طاولات المطعم
INSERT INTO restaurant_tables (table_number, capacity, location) VALUES
    ('1', 4, 'القاعة الرئيسية'),
    ('2', 4, 'القاعة الرئيسية'),
    ('3', 6, 'القاعة الرئيسية'),
    ('4', 2, 'الطابق الثاني'),
    ('5', 8, 'الطابق الثاني'),
    ('VIP1', 6, 'VIP'),
    ('VIP2', 8, 'VIP')
ON CONFLICT DO NOTHING;

-- موردون افتراضيون
INSERT INTO suppliers (supplier_name, contact_name, phone, email) VALUES
    ('مؤسسة المواد الغذائية', 'أحمد محمد', '0501111111', 'food@supplier.com'),
    ('شركة البهارات العربية', 'سالم علي', '0502222222', 'spices@supplier.com'),
    ('مزرعة الخضروات الطازجة', 'محمد سالم', '0503333333', 'veggie@supplier.com')
ON CONFLICT DO NOTHING;

-- مخزون افتراضي
INSERT INTO ingredients (name, unit, current_stock, minimum_stock, reorder_level, unit_cost, supplier_id) VALUES
    ('دجاج طازج', 'كجم', 50, 10, 20, 25, 1),
    ('بهارات مشكلة', 'كجم', 5, 1, 2, 40, 2),
    ('دقيق', 'كجم', 30, 5, 10, 3, 1),
    ('زيت طعام', 'لتر', 20, 5, 8, 8, 1),
    ('أرز بسمتي', 'كجم', 40, 10, 15, 10, 1),
    ('طماطم', 'كجم', 8, 2, 4, 5, 3),
    ('بصل', 'كجم', 15, 3, 5, 3, 3),
    ('ثوم', 'كجم', 3, 0.5, 1, 15, 3),
    ('جبنة موزاريلا', 'كجم', 4, 1, 2, 50, 1),
    ('كريمة طهي', 'لتر', 6, 1, 2, 20, 1)
ON CONFLICT DO NOTHING;
