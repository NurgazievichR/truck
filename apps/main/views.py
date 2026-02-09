from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Contact
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
        
        # Получаем email получателя из контактов
        recipient_email = Contact.objects.filter(type='email').first()
        if not recipient_email or not recipient_email.value:
            print("ERROR: No recipient email configured")
            messages.error(request, 'Contact email not configured. Please contact administrator.')
            return render(request, 'main/contacts.html', {
                'services': services
            })
        
        recipient = recipient_email.value
        print(f"Recipient: {recipient}")
        
        # Получаем названия выбранных услуг
        services_list = []
        if selected_services:
            service_objects = Service.objects.filter(id__in=selected_services)
            services_list = [service.title for service in service_objects]
        
        # Формируем тему и тело письма
        subject = f'New Quote Request from {name}'
        
        email_body = f"""
New quote request submission:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Company: {company if company else 'Not provided'}

Selected Services:
{', '.join(services_list) if services_list else 'None selected'}

Description:
{description if description else 'No description provided'}

---
This message was sent from the quote request form on the website.
"""
        
        try:
            print("Attempting to send email...")
            print(f"From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            print("SUCCESS: Email sent successfully!")
            messages.success(request, 'Thank you! Your quote request has been sent successfully. We will get back to you within 24 hours.')
        except Exception as e:
            print(f"ERROR: Failed to send email - {str(e)}")
            print(f"Error type: {type(e).__name__}")
            logger.error(f'Email send error: {str(e)}', exc_info=True)
            messages.error(request, f'Sorry, there was an error sending your request. Please try again later or contact us directly.')
        
        print("=" * 50)
        return redirect('main:contacts')
    
    return render(request, 'main/contacts.html', {
        'services': services
    })
