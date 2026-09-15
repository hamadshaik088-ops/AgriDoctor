import re

from flask import jsonify


def error_response(message, status=400):
    return jsonify({"error": message}), status


def validate_email(email):
    return "@" in email and "." in email


def validate_mobile_number(mobile_number):
    if not mobile_number:
        return False
    mobile_number = str(mobile_number).strip()
    return bool(re.fullmatch(r"[6-9]\d{9}", mobile_number))
