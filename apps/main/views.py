from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import logging

from .models import Contact, Lead
from .telegram import resolve_notification_chat_id, send_telegram_message
from apps.services.models import Service

logger = logging.getLogger(__name__)


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
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        company = request.POST.get('company', '').strip()
        selected_services = request.POST.getlist('services')
        description = request.POST.get('description', '').strip()

        if not all([name, email]):
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
                'No Telegram chat_id configured; set TELEGRAM_CHAT_ID in .env. lead id=%s',
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
            'No Telegram chat_id configured; chatbot lead id=%s saved only to DB',
            lead.id,
        )

    return JsonResponse({'ok': True, 'id': lead.id, 'telegram_delivered': telegram_ok})
