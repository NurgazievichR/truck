from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import logging
import requests
from .models import Contact
from apps.services.models import Service

logger = logging.getLogger(__name__)


def get_telegram_chat_id_from_username(username):
    """Получает числовой chat_id из обновлений бота по username"""
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


def send_telegram_message(chat_id, message_text):
    """Отправляет сообщение в Telegram через Bot API"""
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
        
        # Отправляем сообщение в Telegram
        telegram_contact = Contact.objects.filter(type='telegram').first()
        if telegram_contact and telegram_contact.value:
            print("Attempting to send Telegram message...")
            print(f"Telegram value from DB: {telegram_contact.value}")
            
            # Проверяем, это username или числовой ID
            chat_id_value = str(telegram_contact.value).strip()
            is_username = not chat_id_value.replace('@', '').replace('t.me/', '').replace('https://t.me/', '').replace('http://t.me/', '').isdigit()
            
            # Если это username, пытаемся получить числовой chat_id
            if is_username:
                print(f"Detected username format, trying to get chat_id...")
                numeric_chat_id = get_telegram_chat_id_from_username(telegram_contact.value)
                if numeric_chat_id:
                    # Сохраняем числовой chat_id в базу для будущих использований
                    telegram_contact.value = numeric_chat_id
                    telegram_contact.save()
                    print(f"Saved numeric chat_id {numeric_chat_id} to database")
                    chat_id_to_use = numeric_chat_id
                else:
                    print("WARNING: Could not find chat_id for username, trying to use username directly...")
                    chat_id_to_use = telegram_contact.value
            else:
                # Уже числовой ID
                chat_id_to_use = telegram_contact.value
            
            telegram_message = f"""
<b>Новая заявка с формы Contact Us</b>

<b>Имя:</b> {name}
<b>Email:</b> {email}
<b>Телефон:</b> {phone if phone else 'Не указан'}
<b>Компания:</b> {company if company else 'Не указана'}

<b>Выбранные услуги:</b>
{', '.join(services_list) if services_list else 'Не выбраны'}

<b>Описание:</b>
{description if description else 'Не указано'}

---
Сообщение отправлено с формы запроса на сайте.
"""
            try:
                telegram_sent = send_telegram_message(chat_id_to_use, telegram_message)
                if telegram_sent:
                    print("SUCCESS: Telegram message sent successfully!")
                    messages.success(request, 'Thank you! Your quote request has been sent successfully. We will get back to you within 24 hours.')
                else:
                    print("ERROR: Failed to send Telegram message")
                    messages.error(request, 'Sorry, there was an error sending your request. Please try again later or contact us directly.')
            except Exception as e:
                print(f"ERROR: Failed to send Telegram message - {str(e)}")
                print(f"Error type: {type(e).__name__}")
                logger.error(f'Telegram send error: {str(e)}', exc_info=True)
                messages.error(request, 'Sorry, there was an error sending your request. Please try again later or contact us directly.')
        else:
            print("ERROR: Telegram contact not configured")
            messages.error(request, 'Telegram contact not configured. Please contact administrator.')
        
        print("=" * 50)
        return redirect('main:contacts')
    
    return render(request, 'main/contacts.html', {
        'services': services
    })
