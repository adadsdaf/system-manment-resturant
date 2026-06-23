-- ====================================================================
-- نظام التراخيص وإدارة المالك - هجرة قاعدة البيانات
-- itQAN Soft - License Management System Migration
-- ====================================================================

-- إضافة دور المالك إن لم يكن موجوداً
INSERT INTO roles (role_name) VALUES ('Owner')
ON CONFLICT (role_name) DO NOTHING;

-- جدول إعدادات الترخيص
CREATE TABLE IF NOT EXISTS license_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL DEFAULT '',
    description TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- جدول الأجهزة المرخصة
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

-- جدول سجل عمليات الترخيص
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

-- البيانات الأولية لإعدادات الترخيص
INSERT INTO license_settings (setting_key, setting_value, description) VALUES
    ('max_pos_devices', '5', 'الحد الأقصى لنقاط البيع المسموحة'),
    ('license_expiry_date', '2027-12-31', 'تاريخ انتهاء الترخيص'),
    ('license_key', 'ITQAN-2025-REST-MGT', 'مفتاح الترخيص الفريد'),
    ('is_license_active', '1', 'حالة الترخيص (1=نشط، 0=معطل)'),
    ('restaurant_name_license', 'مطعم إتقان', 'اسم المطعم في الترخيص'),
    ('license_version', '1.0', 'إصدار الترخيص'),
    ('allow_auto_register', '1', 'السماح بالتسجيل التلقائي للأجهزة الجديدة')
ON CONFLICT (setting_key) DO NOTHING;

-- إنشاء مستخدم المالك الافتراضي إن لم يكن موجوداً
-- كلمة المرور الافتراضية: owner2025
INSERT INTO users (username, full_name, email, password_hash, role_id, branch_id, is_active)
SELECT
    'owner',
    'مالك النظام',
    'owner@restaurant.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    r.role_id,
    1,
    TRUE
FROM roles r WHERE r.role_name = 'Owner'
ON CONFLICT (username) DO NOTHING;
