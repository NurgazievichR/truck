"""
Скрипт для создания тестовых дедлайнов
Запуск: python manage.py shell < apps/deadlines/create_test_data.py
Или: python manage.py shell, затем выполнить код из этого файла
"""
import os
import sys
import django
from datetime import date, timedelta
from random import choice, randint

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.deadlines.models import Deadline


def create_test_deadlines():
    """Создание тестовых дедлайнов"""
    
    # Очистка существующих дедлайнов (опционально)
    # Deadline.objects.all().delete()
    
    document_types = [choice[0] for choice in Deadline.DOCUMENT_TYPE_CHOICES]
    priorities = [choice[0] for choice in Deadline.PRIORITY_CHOICES]
    statuses = [choice[0] for choice in Deadline.STATUS_CHOICES]
    
    clients = [
        'Smith Transport LLC',
        'Rodriguez Fleet',
        'Chen Logistics',
        'Johnson Trucking',
        'Williams Freight',
        'Brown Logistics',
        'Davis Transport',
        None,  # Некоторые без клиента
        None,
    ]
    
    # Создаем дедлайны на разные даты
    today = date.today()
    deadlines_data = []
    
    # Прошлые дедлайны (просроченные)
    for i in range(5):
        deadline_date = today - timedelta(days=randint(1, 30))
        deadlines_data.append({
            'title': f'{choice(document_types)} Filing - Q{randint(1, 4)}',
            'description': f'Quarterly filing deadline for {choice(document_types)} compliance. Ensure all documents are submitted on time.',
            'document_type': choice(document_types),
            'deadline_date': deadline_date,
            'priority': choice(priorities),
            'status': 'overdue' if deadline_date < today else choice(statuses),
            'client_name': choice(clients),
        })
    
    # Текущий месяц
    for i in range(10):
        day = randint(1, 28)
        deadline_date = today.replace(day=day) if day <= today.day or today.month != (today + timedelta(days=32)).month else (today + timedelta(days=randint(0, 28)))
        if deadline_date < today:
            deadline_date = today + timedelta(days=randint(1, 28))
        
        deadlines_data.append({
            'title': f'{choice(document_types)} Renewal',
            'description': f'Annual renewal deadline for {choice(document_types)}. Complete all required documentation.',
            'document_type': choice(document_types),
            'deadline_date': deadline_date,
            'priority': 'high' if (deadline_date - today).days <= 7 else choice(priorities),
            'status': 'pending' if deadline_date >= today else 'in_progress',
            'client_name': choice(clients),
        })
    
    # Следующий месяц
    next_month = today + timedelta(days=32)
    next_month = next_month.replace(day=1)
    for i in range(8):
        day = randint(1, 28)
        deadline_date = next_month.replace(day=day)
        
        deadlines_data.append({
            'title': f'{choice(document_types)} Compliance Check',
            'description': f'Monthly compliance check for {choice(document_types)}. Review all requirements.',
            'document_type': choice(document_types),
            'deadline_date': deadline_date,
            'priority': choice(priorities),
            'status': 'pending',
            'client_name': choice(clients),
        })
    
    # Специфичные дедлайны
    specific_deadlines = [
        {
            'title': 'IFTA Q1 Filing',
            'description': 'First quarter IFTA fuel tax return filing. Submit by end of month.',
            'document_type': 'IFTA',
            'deadline_date': today + timedelta(days=5),
            'priority': 'high',
            'status': 'pending',
            'client_name': 'Smith Transport LLC',
        },
        {
            'title': 'IRP Annual Renewal',
            'description': 'Annual International Registration Plan renewal. Complete registration for all vehicles.',
            'document_type': 'IRP',
            'deadline_date': today + timedelta(days=15),
            'priority': 'high',
            'status': 'in_progress',
            'client_name': 'Rodriguez Fleet',
        },
        {
            'title': 'UCR Registration',
            'description': 'Unified Carrier Registration annual registration deadline.',
            'document_type': 'UCR',
            'deadline_date': today + timedelta(days=20),
            'priority': 'medium',
            'status': 'pending',
        },
        {
            'title': 'FMCSA Safety Audit',
            'description': 'Federal Motor Carrier Safety Administration safety audit preparation.',
            'document_type': 'FMCSA',
            'deadline_date': today + timedelta(days=12),
            'priority': 'high',
            'status': 'in_progress',
            'client_name': 'Chen Logistics',
        },
        {
            'title': 'Form 2290 Filing',
            'description': 'Heavy Vehicle Use Tax Form 2290 filing deadline.',
            'document_type': '2290',
            'deadline_date': today - timedelta(days=3),
            'priority': 'high',
            'status': 'overdue',
            'client_name': 'Johnson Trucking',
        },
    ]
    
    deadlines_data.extend(specific_deadlines)
    
    # Создаем дедлайны
    created_count = 0
    for data in deadlines_data:
        deadline, created = Deadline.objects.get_or_create(
            title=data['title'],
            deadline_date=data['deadline_date'],
            defaults=data
        )
        if created:
            created_count += 1
    
    print(f'✅ Создано {created_count} новых дедлайнов')
    print(f'📊 Всего дедлайнов в базе: {Deadline.objects.count()}')
    
    return created_count


if __name__ == '__main__':
    create_test_deadlines()

