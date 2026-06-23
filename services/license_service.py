from web.db import query, query_scalar
from datetime import date, datetime


# ─── إعدادات الترخيص ─────────────────────────────────────────────

def get_all_settings() -> dict:
    rows = query("SELECT setting_key, setting_value FROM license_settings", fetchall=True) or []
    return {r['setting_key']: r['setting_value'] for r in rows}


def get_setting(key: str, default='') -> str:
    val = query_scalar(
        "SELECT setting_value FROM license_settings WHERE setting_key=%s", (key,)
    )
    return val if val is not None else default


def save_setting(key: str, value: str, description: str = '') -> bool:
    try:
        query(
            """INSERT INTO license_settings (setting_key, setting_value, description, updated_at)
               VALUES (%s, %s, %s, NOW())
               ON CONFLICT (setting_key) DO UPDATE
               SET setting_value=EXCLUDED.setting_value, updated_at=NOW()""",
            (key, value, description), commit=True
        )
        return True
    except Exception:
        return False


# ─── التحقق من الترخيص ────────────────────────────────────────────

def check_license_valid() -> dict:
    settings = get_all_settings()

    if settings.get('is_license_active', '1') != '1':
        return {'valid': False, 'reason': 'disabled',
                'message': 'الترخيص معطل. يرجى التواصل مع الدعم الفني.'}

    expiry_str = settings.get('license_expiry_date', '')
    if expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                return {'valid': False, 'reason': 'expired',
                        'message': f'انتهت صلاحية الترخيص في {expiry_str}. يرجى التواصل مع المدير لتجديد الاشتراك.'}
        except ValueError:
            pass

    return {'valid': True, 'reason': 'ok', 'message': 'الترخيص نشط وصالح.'}


def check_device_licensed(fingerprint: str) -> dict:
    license_check = check_license_valid()
    if not license_check['valid']:
        return license_check

    device = query(
        "SELECT * FROM licensed_devices WHERE machine_fingerprint=%s",
        (fingerprint,), fetchone=True
    )

    if not device:
        allow_auto = get_setting('allow_auto_register', '1')
        max_devices = int(get_setting('max_pos_devices', '5'))
        active_count = count_active_devices()

        if allow_auto == '1' and active_count < max_devices:
            return {'valid': False, 'reason': 'unregistered_auto_ok',
                    'message': 'الجهاز جديد ويمكن تسجيله تلقائياً.'}

        if active_count >= max_devices:
            return {'valid': False, 'reason': 'limit_exceeded',
                    'message': f'تم تجاوز عدد الأجهزة المسموحة ({max_devices}). يرجى ترقية الترخيص.'}

        return {'valid': False, 'reason': 'unregistered',
                'message': 'هذا الجهاز غير مرخص. يرجى التواصل مع المدير.'}

    if not device['is_active']:
        return {'valid': False, 'reason': 'device_disabled',
                'message': f'الجهاز "{device["device_name"]}" معطل. يرجى التواصل مع المدير.'}

    query("UPDATE licensed_devices SET last_seen=NOW() WHERE device_id=%s",
          (device['device_id'],), commit=True)

    return {'valid': True, 'reason': 'ok',
            'message': f'الجهاز "{device["device_name"]}" مرخص وفعال.',
            'device': dict(device)}


def count_active_devices() -> int:
    return query_scalar(
        "SELECT COUNT(*) FROM licensed_devices WHERE is_active=TRUE"
    ) or 0


def auto_register_device(fingerprint: str, device_name: str,
                          ip_address: str = '', added_by: int = None) -> dict:
    max_devices = int(get_setting('max_pos_devices', '5'))
    active_count = count_active_devices()

    if active_count >= max_devices:
        return {'success': False,
                'message': f'تم تجاوز الحد الأقصى للأجهزة ({max_devices}).'}

    existing = query_scalar(
        "SELECT device_id FROM licensed_devices WHERE machine_fingerprint=%s",
        (fingerprint,)
    )
    if existing:
        return {'success': False, 'message': 'البصمة مسجلة مسبقاً.'}

    try:
        query(
            """INSERT INTO licensed_devices
               (device_name, machine_fingerprint, ip_address, is_active, added_by, added_at, last_seen)
               VALUES (%s, %s, %s, TRUE, %s, NOW(), NOW())""",
            (device_name, fingerprint, ip_address, added_by), commit=True
        )
        log_license_action('AUTO_REGISTER', device_name, fingerprint,
                           added_by, ip_address, f'تسجيل تلقائي للجهاز: {device_name}')
        return {'success': True, 'message': f'تم تسجيل الجهاز "{device_name}" بنجاح.'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


# ─── إدارة الأجهزة ────────────────────────────────────────────────

def get_all_devices() -> list:
    return query(
        """SELECT ld.*, u.full_name as added_by_name
           FROM licensed_devices ld
           LEFT JOIN users u ON ld.added_by = u.user_id
           ORDER BY ld.added_at DESC""",
        fetchall=True
    ) or []


def get_device_by_id(device_id: int) -> dict:
    return query(
        "SELECT * FROM licensed_devices WHERE device_id=%s",
        (device_id,), fetchone=True
    )


def add_device(device_name: str, fingerprint: str, ip_address: str = '',
               notes: str = '', added_by: int = None) -> dict:
    existing = query_scalar(
        "SELECT device_id FROM licensed_devices WHERE machine_fingerprint=%s",
        (fingerprint,)
    )
    if existing:
        return {'success': False, 'message': 'هذه البصمة مسجلة مسبقاً في النظام.'}

    max_devices = int(get_setting('max_pos_devices', '5'))
    active_count = count_active_devices()
    if active_count >= max_devices:
        return {'success': False,
                'message': f'تم الوصول إلى الحد الأقصى للأجهزة ({max_devices}). يرجى تعديل إعدادات الترخيص أولاً.'}

    try:
        query(
            """INSERT INTO licensed_devices
               (device_name, machine_fingerprint, ip_address, notes, is_active, added_by, added_at, last_seen)
               VALUES (%s, %s, %s, %s, TRUE, %s, NOW(), NOW())""",
            (device_name, fingerprint, ip_address, notes, added_by), commit=True
        )
        log_license_action('ADD_DEVICE', device_name, fingerprint,
                           added_by, ip_address, f'أضاف جهازاً جديداً: {device_name}')
        return {'success': True, 'message': f'تم إضافة الجهاز "{device_name}" بنجاح.'}
    except Exception as e:
        return {'success': False, 'message': f'خطأ في الإضافة: {str(e)}'}


def toggle_device(device_id: int, performed_by: int = None, ip: str = '') -> dict:
    device = get_device_by_id(device_id)
    if not device:
        return {'success': False, 'message': 'الجهاز غير موجود.'}

    new_status = not device['is_active']
    query("UPDATE licensed_devices SET is_active=%s WHERE device_id=%s",
          (new_status, device_id), commit=True)

    action = 'ENABLE_DEVICE' if new_status else 'DISABLE_DEVICE'
    status_ar = 'تفعيل' if new_status else 'تعطيل'
    log_license_action(action, device['device_name'], device['machine_fingerprint'],
                       performed_by, ip, f'{status_ar} الجهاز: {device["device_name"]}')

    return {'success': True,
            'message': f'تم {"تفعيل" if new_status else "تعطيل"} الجهاز "{device["device_name"]}" بنجاح.',
            'new_status': new_status}


def delete_device(device_id: int, performed_by: int = None, ip: str = '') -> dict:
    device = get_device_by_id(device_id)
    if not device:
        return {'success': False, 'message': 'الجهاز غير موجود.'}

    query("DELETE FROM licensed_devices WHERE device_id=%s", (device_id,), commit=True)
    log_license_action('DELETE_DEVICE', device['device_name'], device['machine_fingerprint'],
                       performed_by, ip, f'حذف الجهاز: {device["device_name"]}')

    return {'success': True, 'message': f'تم حذف الجهاز "{device["device_name"]}" بنجاح.'}


# ─── سجل عمليات الترخيص ──────────────────────────────────────────

def log_license_action(action_type: str, device_name: str = '',
                        fingerprint: str = '', performed_by: int = None,
                        ip_address: str = '', details: str = '') -> None:
    try:
        query(
            """INSERT INTO license_audit_log
               (action_type, device_name, machine_fingerprint, performed_by, ip_address, details, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
            (action_type, device_name, fingerprint or '', performed_by, ip_address or '', details),
            commit=True
        )
    except Exception:
        pass


def get_audit_log(limit: int = 200) -> list:
    return query(
        """SELECT al.*, u.full_name as user_name
           FROM license_audit_log al
           LEFT JOIN users u ON al.performed_by = u.user_id
           ORDER BY al.created_at DESC
           LIMIT %s""",
        (limit,), fetchall=True
    ) or []


# ─── تقرير الترخيص ───────────────────────────────────────────────

def get_license_report() -> dict:
    settings = get_all_settings()
    devices = get_all_devices()
    audit = get_audit_log(limit=10)
    active_count = count_active_devices()

    expiry_str = settings.get('license_expiry_date', '')
    days_remaining = None
    if expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            delta = (expiry - date.today()).days
            days_remaining = delta
        except ValueError:
            pass

    return {
        'settings': settings,
        'devices': [dict(d) for d in devices],
        'audit': [dict(a) for a in audit],
        'active_count': active_count,
        'max_devices': int(settings.get('max_pos_devices', '5')),
        'days_remaining': days_remaining,
        'is_active': settings.get('is_license_active', '1') == '1',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
