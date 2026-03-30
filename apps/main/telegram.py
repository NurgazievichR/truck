import logging
import re

from django.conf import settings

from .models import Contact

try:
    import requests
except ImportError:  # pragma: no cover - depends on environment
    requests = None


logger = logging.getLogger(__name__)


def _strip_t_me_prefix(value: str) -> str:
    s = str(value or '').strip()
    for prefix in ('https://t.me/', 'http://t.me/', 't.me/'):
        if s.startswith(prefix):
            return s[len(prefix):].strip()
    return s


def _build_public_telegram_url(raw_value: str) -> str:
    raw = str(raw_value or '').strip()
    if not raw:
        return ''

    if raw.startswith(('https://t.me/', 'http://t.me/')):
        return raw

    inner = _strip_t_me_prefix(raw).lstrip('@')
    if not inner:
        return ''

    if raw.startswith('+') and re.fullmatch(r'\+\d{8,}', raw):
        return f'https://t.me/{raw}'

    if re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{3,31}', inner):
        return f'https://t.me/{inner}'

    return ''


def resolve_public_telegram_url() -> str:
    public_url = str(getattr(settings, 'TELEGRAM_PUBLIC_URL', '') or '').strip()
    if public_url:
        return _build_public_telegram_url(public_url)

    contact = Contact.objects.filter(type='telegram').first()
    if not contact:
        return ''

    return _build_public_telegram_url(contact.value)


def resolve_notification_chat_id() -> str | None:
    raw = str(getattr(settings, 'TELEGRAM_CHAT_ID', '') or '').strip()
    if raw:
        if re.fullmatch(r'-?\d+', raw):
            return raw
        logger.warning('TELEGRAM_CHAT_ID must be a numeric chat_id.')

    contact = Contact.objects.filter(type='telegram').first()
    contact_value = str((contact.value if contact else '') or '').strip()
    if re.fullmatch(r'-?\d+', contact_value):
        return contact_value

    return None


def send_telegram_message(chat_id, message_text):
    if requests is None:
        logger.warning('requests is not installed; Telegram sending is unavailable.')
        return False

    bot_token = str(getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or '').strip()
    if not bot_token:
        logger.warning('TELEGRAM_BOT_TOKEN is not configured.')
        return False

    chat_id = str(chat_id or '').strip()
    if not re.fullmatch(r'-?\d+', chat_id):
        logger.warning('Telegram notification requires a numeric chat_id.')
        return False

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    plain_text = (
        str(message_text or '')
        .replace('<b>', '')
        .replace('</b>', '')
        .replace('<br>', '\n')
    )

    try:
        response = requests.post(
            url,
            json={
                'chat_id': chat_id,
                'text': str(message_text or ''),
                'parse_mode': 'HTML',
            },
            timeout=10,
        )
        if response.ok:
            return True

        error_description = ''
        try:
            error_description = response.json().get('description', '')
        except ValueError:
            error_description = response.text
        logger.error('Telegram API error %s: %s', response.status_code, error_description)

        fallback = requests.post(
            url,
            json={'chat_id': chat_id, 'text': plain_text},
            timeout=10,
        )
        if fallback.ok:
            return True

        fallback_description = ''
        try:
            fallback_description = fallback.json().get('description', '')
        except ValueError:
            fallback_description = fallback.text
        logger.error(
            'Telegram fallback error %s: %s',
            fallback.status_code,
            fallback_description,
        )
        return False
    except requests.exceptions.RequestException as exc:
        logger.error('Telegram send error: %s', exc, exc_info=True)
        return False
