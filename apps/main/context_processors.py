from .telegram import resolve_public_telegram_url


def telegram_contact(request):
    return {'tg_url': resolve_public_telegram_url()}
