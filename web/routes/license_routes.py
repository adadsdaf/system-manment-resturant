from flask import Blueprint, render_template, request, jsonify, session
from web.routes.dashboard_routes import login_required
from services.license_service import (
    get_all_settings, get_setting, save_setting,
    get_all_devices, add_device, toggle_device, delete_device,
    check_license_valid, count_active_devices, get_audit_log,
    get_license_report, log_license_action, auto_register_device
)
from services.fingerprint_service import generate_web_fingerprint

license_bp = Blueprint('license', __name__)


def owner_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if session.get('role') not in ('Owner', 'Admin'):
            return render_template('403.html')
        return f(*args, **kwargs)
    return decorated


# ─── صفحة إدارة التراخيص ─────────────────────────────────────────

@license_bp.route('/license')
@owner_required
def index():
    settings = get_all_settings()
    devices = get_all_devices()
    audit = get_audit_log(limit=50)
    active_count = count_active_devices()
    license_status = check_license_valid()

    from datetime import date
    expiry_str = settings.get('license_expiry_date', '')
    days_remaining = None
    if expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            days_remaining = (expiry - date.today()).days
        except ValueError:
            pass

    return render_template(
        'license.html',
        settings=settings,
        devices=devices,
        audit=audit,
        active_count=active_count,
        max_devices=int(settings.get('max_pos_devices', '5')),
        license_status=license_status,
        days_remaining=days_remaining,
    )


# ─── API: إضافة جهاز ─────────────────────────────────────────────

@license_bp.route('/license/add_device', methods=['POST'])
@owner_required
def add_device_api():
    d = request.get_json() or {}
    device_name = (d.get('device_name') or '').strip()
    fingerprint = (d.get('fingerprint') or '').strip()
    ip_address = (d.get('ip_address') or request.remote_addr or '').strip()
    notes = (d.get('notes') or '').strip()

    if not device_name or not fingerprint:
        return jsonify({'success': False, 'message': 'اسم الجهاز والبصمة مطلوبان.'})

    result = add_device(
        device_name=device_name,
        fingerprint=fingerprint,
        ip_address=ip_address,
        notes=notes,
        added_by=session.get('user_id')
    )
    return jsonify(result)


# ─── API: تفعيل/تعطيل جهاز ───────────────────────────────────────

@license_bp.route('/license/toggle_device', methods=['POST'])
@owner_required
def toggle_device_api():
    d = request.get_json() or {}
    device_id = d.get('device_id')
    if not device_id:
        return jsonify({'success': False, 'message': 'معرّف الجهاز مطلوب.'})
    result = toggle_device(
        device_id=int(device_id),
        performed_by=session.get('user_id'),
        ip=request.remote_addr or ''
    )
    return jsonify(result)


# ─── API: حذف جهاز ───────────────────────────────────────────────

@license_bp.route('/license/delete_device', methods=['POST'])
@owner_required
def delete_device_api():
    d = request.get_json() or {}
    device_id = d.get('device_id')
    if not device_id:
        return jsonify({'success': False, 'message': 'معرّف الجهاز مطلوب.'})
    result = delete_device(
        device_id=int(device_id),
        performed_by=session.get('user_id'),
        ip=request.remote_addr or ''
    )
    return jsonify(result)


# ─── API: حفظ إعدادات الترخيص ────────────────────────────────────

@license_bp.route('/license/save_settings', methods=['POST'])
@owner_required
def save_settings_api():
    d = request.get_json() or {}
    errors = []
    saved = []

    fields = {
        'max_pos_devices': 'الحد الأقصى للأجهزة',
        'license_expiry_date': 'تاريخ انتهاء الترخيص',
        'license_key': 'مفتاح الترخيص',
        'is_license_active': 'حالة الترخيص',
        'restaurant_name_license': 'اسم المطعم',
        'allow_auto_register': 'التسجيل التلقائي',
    }

    for key, label in fields.items():
        val = d.get(key)
        if val is not None:
            if save_setting(key, str(val)):
                saved.append(label)
            else:
                errors.append(label)

    if errors:
        return jsonify({'success': False, 'message': f'فشل حفظ: {", ".join(errors)}'})

    log_license_action(
        'UPDATE_SETTINGS', '', '',
        session.get('user_id'),
        request.remote_addr or '',
        f'تحديث إعدادات الترخيص: {", ".join(saved)}'
    )
    return jsonify({'success': True, 'message': 'تم حفظ الإعدادات بنجاح.'})


# ─── API: تقرير الترخيص ──────────────────────────────────────────

@license_bp.route('/license/report')
@owner_required
def report():
    report_data = get_license_report()
    return jsonify(report_data)


# ─── API: التحقق من بصمة الجهاز (للاستخدام الداخلي) ─────────────

@license_bp.route('/license/check_device', methods=['POST'])
@login_required
def check_device_api():
    d = request.get_json() or {}
    fingerprint = (d.get('fingerprint') or '').strip()
    device_name = (d.get('device_name') or 'جهاز جديد').strip()

    if not fingerprint:
        fingerprint = generate_web_fingerprint(
            request.remote_addr or '',
            request.headers.get('User-Agent', '')
        )

    from services.license_service import check_device_licensed
    result = check_device_licensed(fingerprint)

    if not result['valid'] and result.get('reason') == 'unregistered_auto_ok':
        auto_result = auto_register_device(
            fingerprint=fingerprint,
            device_name=device_name,
            ip_address=request.remote_addr or '',
            added_by=session.get('user_id')
        )
        if auto_result['success']:
            result = {'valid': True, 'reason': 'auto_registered',
                      'message': f'تم تسجيل الجهاز "{device_name}" تلقائياً.'}

    return jsonify(result)


# ─── API: سجل العمليات ────────────────────────────────────────────

@license_bp.route('/license/audit_log')
@owner_required
def audit_log_api():
    limit = int(request.args.get('limit', 100))
    logs = get_audit_log(limit=limit)
    return jsonify([dict(r) for r in logs])


# ─── API: توليد مفتاح ترخيص جديد ────────────────────────────────

@license_bp.route('/license/generate_key', methods=['POST'])
@owner_required
def generate_key_api():
    from utils.encryption_utils import generate_license_key
    new_key = generate_license_key('ITQAN')
    log_license_action(
        'GENERATE_KEY', '', '',
        session.get('user_id'),
        request.remote_addr or '',
        f'توليد مفتاح ترخيص جديد: {new_key}'
    )
    return jsonify({'success': True, 'key': new_key})
