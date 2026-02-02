from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Deadline


def deadlines_calendar(request):
    """Публичная страница с календарем дедлайнов"""
    
    # Получаем параметры фильтрации
    document_type = request.GET.get('type', '')
    month = request.GET.get('month', '')
    year = request.GET.get('year', '')
    
    # Получаем текущую дату
    today = timezone.now().date()
    
    # Определяем месяц и год для отображения
    if month and year:
        try:
            display_month = int(month)
            display_year = int(year)
        except ValueError:
            display_month = today.month
            display_year = today.year
    else:
        display_month = today.month
        display_year = today.year
    
    # Получаем все дедлайны
    deadlines = Deadline.objects.all().order_by('deadline_date', 'priority')
    
    # Фильтрация по типу документа
    if document_type:
        deadlines = deadlines.filter(document_type=document_type)
    
    # Фильтрация по месяцу и году
    # Всегда фильтруем по выбранному месяцу для календаря
    deadlines = deadlines.filter(
        deadline_date__year=display_year,
        deadline_date__month=display_month
    )
    
    # Группируем дедлайны по датам для календаря
    deadlines_by_date = {}
    for deadline in deadlines:
        date_key = deadline.deadline_date.isoformat()
        if date_key not in deadlines_by_date:
            deadlines_by_date[date_key] = []
        deadlines_by_date[date_key].append(deadline)
    
    # Получаем список типов документов для фильтра
    document_types = Deadline.DOCUMENT_TYPE_CHOICES
    
    # Статистика
    total_deadlines = Deadline.objects.count()
    upcoming_deadlines = Deadline.objects.filter(
        deadline_date__gte=today,
        status__in=['pending', 'in_progress']
    ).count()
    # Просроченные: дата прошла И статус не completed
    overdue_deadlines = Deadline.objects.filter(
        deadline_date__lt=today
    ).exclude(
        status='completed'
    ).count()
    
    # Генерируем календарь для выбранного месяца
    calendar_data = generate_calendar(display_year, display_month, deadlines_by_date, today)
    
    context = {
        'deadlines': deadlines,
        'deadlines_by_date': deadlines_by_date,
        'document_types': document_types,
        'selected_type': document_type,
        'display_month': display_month,
        'display_year': display_year,
        'today': today,
        'calendar_data': calendar_data,
        'total_deadlines': total_deadlines,
        'upcoming_deadlines': upcoming_deadlines,
        'overdue_deadlines': overdue_deadlines,
    }
    
    # Проверяем, это AJAX запрос?
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Возвращаем только календарь и список дедлайнов
        return render(request, 'deadlines/calendar_partial.html', context)
    
    return render(request, 'deadlines/calendar.html', context)


def generate_calendar(year, month, deadlines_by_date, today):
    """Генерирует данные календаря для указанного месяца"""
    # Первый день месяца
    first_day = datetime(year, month, 1).date()
    
    # Количество дней в месяце
    days_in_month = monthrange(year, month)[1]
    
    # День недели первого дня (0 = понедельник, 6 = воскресенье)
    first_weekday = first_day.weekday()
    
    # Создаем календарь
    calendar = []
    week = []
    
    # Добавляем пустые ячейки для дней до начала месяца
    for _ in range(first_weekday):
        week.append(None)
    
    # Добавляем дни месяца
    for day in range(1, days_in_month + 1):
        current_date = datetime(year, month, day).date()
        date_key = current_date.isoformat()
        
        week.append({
            'date': current_date,
            'day': day,
            'deadlines': deadlines_by_date.get(date_key, []),
            'is_today': current_date == today,
            'is_past': current_date < today,
        })
        
        # Если неделя заполнена, добавляем в календарь
        if len(week) == 7:
            calendar.append(week)
            week = []
    
    # Добавляем оставшиеся дни следующего месяца
    if week:
        while len(week) < 7:
            week.append(None)
        calendar.append(week)
    
    return calendar
