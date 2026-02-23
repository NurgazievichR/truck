from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import logging
import requests
from .models import Contact
from apps.services.models import Service

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message_text):
    """Отправляет сообщение в Telegram через Bot API"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.warning('TELEGRAM_BOT_TOKEN not configured')
        return False
    
    if not chat_id:
        logger.warning('Telegram chat_id not provided')
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                'chat_id': chat_id,
                'text': message_text,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Telegram send error: {str(e)}', exc_info=True)
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
                telegram_sent = send_telegram_message(telegram_contact.value, telegram_message)
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
