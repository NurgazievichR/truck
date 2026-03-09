from .models import Contact


def telegram_contact(request):
    """Exposes telegram handle to all templates via {{ tg_handle }}"""
    contact = Contact.objects.filter(type='telegram').first()
    handle = ''
    if contact and contact.value:
        raw = str(contact.value).strip()
        # Normalize to plain username (strip @, URLs, numeric IDs)
        raw = raw.replace('https://t.me/', '').replace('http://t.me/', '').replace('t.me/', '').lstrip('@')
        if raw.isdigit():
            raw = ''
        handle = raw
    return {'tg_handle': handle or '+13123889569'}
