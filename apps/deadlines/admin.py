from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Deadline


@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'document_type',
        'deadline_date',
        'priority_badge',
        'status_badge',
        'days_until',
        'client_name',
        'priority',
        'status',
        'created_at',
        'delete_button'
    ]
    list_filter = [
        'document_type',
        'priority',
        'status',
        'deadline_date',
        'created_at'
    ]
    search_fields = [
        'title',
        'description',
        'client_name',
        'document_type'
    ]
    date_hierarchy = 'deadline_date'
    list_editable = ['status', 'priority']
    readonly_fields = ['created_at', 'updated_at', 'days_until_deadline_display', 'urgency_color_display']
    actions = None  # Отключаем actions dropdown
    
    def get_actions(self, request):
        """Отключаем actions полностью"""
        return {}
    
    fieldsets = (
        ('Main Information', {
            'fields': ('title', 'description', 'document_type')
        }),
        ('Deadline Details', {
            'fields': ('deadline_date', 'priority', 'status', 'reminder_days')
        }),
        ('Client Information', {
            'fields': ('client_name',),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': ('days_until_deadline_display', 'urgency_color_display'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def priority_badge(self, obj):
        """Цветной бейдж приоритета"""
        colors = {
            'high': 'red',
            'medium': 'orange',
            'low': 'green'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        """Цветной бейдж статуса"""
        colors = {
            'pending': 'gray',
            'in_progress': 'blue',
            'completed': 'green',
            'overdue': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def days_until(self, obj):
        """Отображение дней до дедлайна"""
        days = obj.days_until_deadline
        if days < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Overdue ({} days)</span>',
                abs(days)
            )
        elif days == 0:
            return mark_safe('<span style="color: orange; font-weight: bold;">Today!</span>')
        else:
            return f"{days} days"
    days_until.short_description = 'Days Until'
    
    def days_until_deadline_display(self, obj):
        """Отображение дней до дедлайна в детальном виде"""
        days = obj.days_until_deadline
        if days < 0:
            return f"Overdue by {abs(days)} days"
        elif days == 0:
            return "Due today!"
        else:
            return f"{days} days remaining"
    days_until_deadline_display.short_description = 'Time Until Deadline'
    
    def urgency_color_display(self, obj):
        """Отображение цвета срочности"""
        color = obj.urgency_color
        color_names = {
            'red': 'Red (Overdue)',
            'orange': 'Orange (Urgent - 7 days or less)',
            'yellow': 'Yellow (Soon - 30 days or less)',
            'green': 'Green (OK - more than 30 days)'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            color_names.get(color, color)
        )
        urgency_color_display.short_description = 'Urgency Level'
    
    def delete_button(self, obj):
        """Кнопка удаления для каждой записи"""
        delete_url = reverse('admin:deadlines_deadline_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px; display: inline-block;">Delete</a>',
            delete_url
        )
    delete_button.short_description = 'Actions'
