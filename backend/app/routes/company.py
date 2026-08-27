from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import CompanyProfile

company_bp = Blueprint('company_api', __name__, url_prefix='/api/company-profile')

FIELDS = ['company_name','legal_name','tax_number','tax_office','phone','email','website','address','city','district']


def serialize(profile):
    return {field: getattr(profile, field) or '' for field in FIELDS} | {'id': profile.id}


@company_bp.get('')
def get_profile():
    profile = CompanyProfile.query.first()
    if profile is None:
        profile = CompanyProfile()
        db.session.add(profile)
        db.session.commit()
    return jsonify(serialize(profile))


@company_bp.put('')
def update_profile():
    data = request.get_json(silent=True) or {}
    profile = CompanyProfile.query.first()
    if profile is None:
        profile = CompanyProfile()
        db.session.add(profile)

    company_name = str(data.get('company_name', '')).strip()
    if not company_name:
        return jsonify({'error': 'İşletme adı zorunludur.'}), 400

    for field in FIELDS:
        if field in data:
            setattr(profile, field, str(data.get(field) or '').strip())

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'İşletme bilgileri kaydedilemedi.'}), 500

    return jsonify(serialize(profile))
