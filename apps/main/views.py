from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import logging
import re

try:
    import requests
except ImportError:
    requests = None  # pip install requests — для отправки в Telegram

from .models import Contact, Lead
from apps.services.models import Service

logger = logging.getLogger(__name__)


def get_telegram_chat_id_from_username(username):
    """Получает числовой chat_id из обновлений бота по username"""
    if requests is None:
        return None
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return None
    
    # Убираем префиксы и @
    username = str(username).strip()
    if username.startswith('t.me/'):
        username = username.replace('t.me/', '')
    elif username.startswith('https://t.me/'):
        username = username.replace('https://t.me/', '')
    elif username.startswith('http://t.me/'):
        username = username.replace('http://t.me/', '')
    if username.startswith('@'):
        username = username[1:]
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                # Ищем обновление с нужным username
                updates = data['result']
                for update in reversed(updates):  # Идем с конца (последние обновления)
                    if 'message' in update:
                        chat = update['message'].get('chat', {})
                        chat_username = chat.get('username', '').lower()
                        if chat_username == username.lower():
                            chat_id = chat.get('id')
                            if chat_id:
                                print(f"Found chat_id {chat_id} for username @{username}")
                                return str(chat_id)
    except Exception as e:
        logger.error(f'Error getting chat_id from updates: {str(e)}')
    return None


def _strip_t_me_prefix(value: str) -> str:
    s = value.strip()
    for pref in ('https://t.me/', 'http://t.me/', 't.me/'):
        if s.startswith(pref):
            s = s[len(pref) :]
            break
    return s.strip()


def resolve_notification_chat_id():
    """
    Куда слать уведомления бота: числовой chat_id (или @username как запасной вариант).

    Важно: ссылка вида t.me/+1XXXXXXXXXX — это не chat_id для Bot API. Нужен числовой id
    (после того как получатель написал боту /start — см. @userinfobot) или TELEGRAM_CHAT_ID в .env.
    """
    cfg = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    if cfg is not None:
        cfg = str(cfg).strip()
        if cfg:
            if re.fullmatch(r'-?\d+', cfg):
                return cfg
            logger.warning('TELEGRAM_CHAT_ID must be a numeric chat_id; ignoring value and using Contact if set.')

    contact = Contact.objects.filter(type='telegram').first()
    if not contact or not (contact.value or '').strip():
        return None

    raw = contact.value.strip()

    if re.fullmatch(r'-?\d+', raw):
        return raw

    inner = _strip_t_me_prefix(raw)

    # Deep link по номеру телефона — Bot API не принимает это как chat_id
    if re.fullmatch(r'\+\d{8,}', inner):
        logger.warning(
            'Telegram Contact value is a phone deep link (%s…). '
            'Set TELEGRAM_CHAT_ID in .env to your numeric chat_id after /start with the bot.',
            inner[:6],
        )
        return None

    digits_only = inner.lstrip('+')
    if re.fullmatch(r'\d+', digits_only) and len(digits_only) >= 6:
        # Частая ошибка: положить номер телефона без + — это не Telegram user id
        if len(digits_only) == 11 and digits_only.startswith('1'):
            logger.warning(
                'Telegram Contact value looks like a US phone number, not a chat_id. '
                'Use TELEGRAM_CHAT_ID (numeric id from @userinfobot after /start).'
            )
            return None
        return digits_only

    username = inner.lstrip('@')
    if re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{3,31}', username):
        numeric = get_telegram_chat_id_from_username(username)
        if numeric:
            return numeric
        return '@' + username

    return None


def send_telegram_message(chat_id, message_text):
    """Отправляет сообщение в Telegram через Bot API"""
    if requests is None:
        logger.warning('requests не установлен; для Telegram: pip install requests')
        return False
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.warning('TELEGRAM_BOT_TOKEN not configured')
        return False
    
    if not chat_id:
        logger.warning('Telegram chat_id not provided')
        return False
    
    # Нормализуем chat_id - убираем лишние символы
    chat_id = str(chat_id).strip()
    
    # Убираем префиксы URL если есть
    if chat_id.startswith('https://t.me/'):
        chat_id = chat_id.replace('https://t.me/', '')
    elif chat_id.startswith('http://t.me/'):
        chat_id = chat_id.replace('http://t.me/', '')
    elif chat_id.startswith('t.me/'):
        chat_id = chat_id.replace('t.me/', '')
    
    # Убираем @ если есть в начале
    if chat_id.startswith('@'):
        chat_id = chat_id[1:]
    
    # Если это числовой ID, оставляем как есть
    # Если это username, добавляем @ обратно (Telegram API принимает оба формата)
    if not chat_id.isdigit():
        # Это username, добавляем @ если его нет
        if not chat_id.startswith('@'):
            chat_id = '@' + chat_id
    
    print(f"Normalized chat_id: {chat_id}")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Экранируем специальные символы для HTML
    import html
    # Экранируем только текст внутри тегов, но не сами теги
    # Для этого используем более простой подход - убираем parse_mode если есть проблемы
    safe_message = message_text
    
    try:
        # Сначала пробуем с HTML
        response = requests.post(
            url,
            json={
                'chat_id': chat_id,  # Уже нормализован
                'text': safe_message,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        
        # Если ошибка, логируем детали
        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            error_description = error_data.get('description', 'Unknown error')
            print(f"Telegram API Error: {response.status_code}")
            print(f"Error description: {error_description}")
            print(f"Full response: {error_data}")
            logger.error(f'Telegram API error {response.status_code}: {error_description}')
            
            # Пробуем отправить без parse_mode
            print("Trying without parse_mode...")
            response = requests.post(
                url,
                json={
                    'chat_id': chat_id,
                    'text': safe_message.replace('<b>', '*').replace('</b>', '*').replace('<br>', '\n'),
                    'parse_mode': 'Markdown'
                },
                timeout=10
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_description = error_data.get('description', 'Unknown error')
                print(f"Telegram API Error (Markdown): {response.status_code}")
                print(f"Error description: {error_description}")
                logger.error(f'Telegram API error (Markdown) {response.status_code}: {error_description}')
                
                # Последняя попытка - без форматирования
                print("Trying without any formatting...")
                plain_text = message_text.replace('<b>', '').replace('</b>', '').replace('<br>', '\n')
                response = requests.post(
                    url,
                    json={
                        'chat_id': chat_id,
                        'text': plain_text
                    },
                    timeout=10
                )
        
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_details = f"{error_details} - {error_data.get('description', '')}"
            except:
                pass
        print(f"Telegram send error: {error_details}")
        logger.error(f'Telegram send error: {error_details}', exc_info=True)
        return False


def index(request):
    """Главная страница"""
    services = Service.objects.all()[:6]  # Первые 6 услуг для главной
    contacts = Contact.objects.all()
    phone_contact = Contact.objects.filter(type='phone').first()
    return render(request, 'main/index.html', {
        'services': services,
        'contacts': contacts,
        'phone_contact': phone_contact
    })


def about(request):
    """Страница О компании"""
    return render(request, 'main/about.html')


def contacts(request):
    """Страница Request a Quote"""
    services = Service.objects.all()
    
    if request.method == 'POST':
        print("=" * 50)
        print("POST REQUEST RECEIVED - Quote Form Submission")
        print("=" * 50)
        
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        company = request.POST.get('company', '').strip()
        selected_services = request.POST.getlist('services')
        description = request.POST.get('description', '').strip()
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Company: {company}")
        print(f"Selected Services: {selected_services}")
        print(f"Description: {description[:50]}...")
        
        # Валидация
        if not all([name, email]):
            print("ERROR: Missing required fields")
            messages.error(request, 'Please fill in all required fields (Name and Email).')
            return render(request, 'main/contacts.html', {
                'services': services
            })
        
        # Получаем названия выбранных услуг
        services_list = []
        if selected_services:
            service_objects = Service.objects.filter(id__in=selected_services)
            services_list = [service.title for service in service_objects]

        services_line = ', '.join(services_list) if services_list else '—'
        lead_message = f'Услуги: {services_line}\nОписание: {description or "—"}'
        lead = Lead.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=lead_message,
            source=Lead.SOURCE_FORM,
        )
        logger.info('Contact form lead saved id=%s', lead.id)

        telegram_message = f"""
<b>Новая заявка с формы Contact Us</b>

<b>Имя:</b> {name}
<b>Email:</b> {email}
<b>Телефон:</b> {phone if phone else 'Не указан'}
<b>Компания:</b> {company if company else 'Не указана'}

<b>Выбранные услуги:</b>
{services_line}

<b>Описание:</b>
{description if description else 'Не указано'}

---
Сообщение отправлено с формы запроса на сайте.
"""

        bot_token = (getattr(settings, 'TELEGRAM_BOT_TOKEN', None) or '').strip()
        chat_id_to_use = resolve_notification_chat_id()

        if not bot_token:
            logger.warning('TELEGRAM_BOT_TOKEN not set; lead id=%s saved without Telegram', lead.id)
            messages.success(
                request,
                'Thank you! Your request was received. We will get back to you within 24 hours.',
            )
        elif not chat_id_to_use:
            logger.warning(
                'No Telegram chat_id (set TELEGRAM_CHAT_ID in .env or valid Contact telegram); lead id=%s',
                lead.id,
            )
            messages.success(
                request,
                'Thank you! Your request was received. We will get back to you within 24 hours.',
            )
        else:
            try:
                telegram_sent = send_telegram_message(chat_id_to_use, telegram_message)
                if telegram_sent:
                    messages.success(
                        request,
                        'Thank you! Your quote request has been sent successfully. We will get back to you within 24 hours.',
                    )
                else:
                    logger.error('Telegram send failed for contact form lead id=%s', lead.id)
                    messages.warning(
                        request,
                        'Your request was saved. We could not send an instant notification — we will still contact you shortly.',
                    )
            except Exception as e:
                logger.error('Telegram send error: %s', str(e), exc_info=True)
                messages.warning(
                    request,
                    'Your request was saved. We could not send an instant notification — we will still contact you shortly.',
                )
        
        print("=" * 50)
        return redirect('main:contacts')
    
    return render(request, 'main/contacts.html', {
        'services': services
    })


@require_POST
def chatbot_lead(request):
    """AJAX endpoint for chatbot lead form — saves to DB and sends Telegram"""
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('description', '').strip()

    if not name or not email:
        return JsonResponse({'ok': False, 'error': 'name and email required'}, status=400)

    # Save lead to DB
    lead = Lead.objects.create(name=name, email=email, phone=phone, message=message, source=Lead.SOURCE_CHATBOT)

    bot_token = (getattr(settings, 'TELEGRAM_BOT_TOKEN', None) or '').strip()
    chat_id_to_use = resolve_notification_chat_id()
    tg_message = (
        f"<b>Новая заявка с чат-бота</b>\n\n"
        f"<b>Имя:</b> {name}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Телефон:</b> {phone if phone else 'не указан'}\n"
        f"<b>Сообщение:</b> {message if message else '—'}"
    )
    telegram_ok = False
    if bot_token and chat_id_to_use:
        telegram_ok = bool(send_telegram_message(chat_id_to_use, tg_message))
        if not telegram_ok:
            logger.error('Telegram send failed for chatbot lead id=%s', lead.id)
    elif not bot_token:
        logger.warning('TELEGRAM_BOT_TOKEN not set; chatbot lead id=%s saved only to DB', lead.id)
    else:
        logger.warning(
            'No Telegram chat_id; chatbot lead id=%s saved only to DB (set TELEGRAM_CHAT_ID or fix Contact)',
            lead.id,
        )

    return JsonResponse({'ok': True, 'id': lead.id, 'telegram_delivered': telegram_ok})
