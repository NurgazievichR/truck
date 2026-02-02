from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from apps.services.models import Service


def index(request):
    """Главная страница"""
    services = Service.objects.all()[:6]  # Первые 6 услуг для главной
    contacts = Contact.objects.all()
    return render(request, 'main/index.html', {
        'services': services,
        'contacts': contacts
    })


def about(request):
    """Страница О компании"""
    return render(request, 'main/about.html')


def contacts(request):
    """Страница Контакты"""
    contact_list = Contact.objects.all().order_by('type')
    
    if request.method == 'POST':
        # Получаем данные из формы
        email_to = request.POST.get('email_to', 'both')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Валидация
        if not all([first_name, last_name, email, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'main/contacts.html', {
                'contacts': contact_list
            })
        
        # Получаем email получателя из контактов
        recipient_email = Contact.objects.filter(type='email').first()
        if not recipient_email or not recipient_email.value:
            messages.error(request, 'Contact email not configured. Please contact administrator.')
            return render(request, 'main/contacts.html', {
                'contacts': contact_list
            })
        
        recipient = recipient_email.value
        
        # Формируем тему и тело письма
        subject = f'New Contact Form Submission from {first_name} {last_name}'
        
        email_body = f"""
New contact form submission:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Send to: {email_to.upper()}

Message:
{message}

---
This message was sent from the contact form on the website.
"""
        
        try:
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            messages.success(request, 'Thank you! Your message has been sent successfully. We will get back to you soon.')
        except Exception as e:
            messages.error(request, f'Sorry, there was an error sending your message. Please try again later or contact us directly.')
        
        return redirect('main:contacts')
    
    return render(request, 'main/contacts.html', {
        'contacts': contact_list
    })
