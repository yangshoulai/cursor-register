
import datetime
import tzlocal
import re
import requests
from conf import MAIL_ADDR_AT_TEMP_MAIL_PLUS, MAIL_PIN_AT_TEMP_MAIL_PLUS, MAIL_DOMAIN

_session = requests.session()


def get_latest_cursor_verification_code(email_from: str):
    '''获取最新的 cursor 验证码'''
    mail_list_url = f"https://tempmail.plus/api/mails?email={MAIL_ADDR_AT_TEMP_MAIL_PLUS}&limit=20&epin={MAIL_PIN_AT_TEMP_MAIL_PLUS}"
    mail_list = _session.get(mail_list_url).json()
    if not mail_list.get("result") or not mail_list.get("first_id"):
        return None
    first_id = mail_list.get("first_id")
    mail_detail_url = f"https://tempmail.plus/api/mails/{first_id}?email={MAIL_ADDR_AT_TEMP_MAIL_PLUS}&epin={MAIL_PIN_AT_TEMP_MAIL_PLUS}"
    mail_detail = _session.get(mail_detail_url).json()
    from_name = mail_detail.get("from_name", "")
    to = mail_detail.get("to", "")
    text = mail_detail.get("text", "")
    if not mail_detail.get("result") or not text or from_name != "Cursor" or email_from != to:
        return None
    code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", text)
    if code_match:
        return code_match.group()
    return None
