from django.db import models
from django.utils import timezone


class Deadline(models.Model):
    """Модель для дедлайнов по compliance документам"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('IFTA', 'IFTA (International Fuel Tax Agreement)'),
        ('IRP', 'IRP (International Registration Plan)'),
        ('UCR', 'UCR (Unified Carrier Registration)'),
        ('FMCSA', 'FMCSA (Federal Motor Carrier Safety Administration)'),
        ('DOT', 'DOT (Department of Transportation)'),
        ('HVUT', 'HVUT (Heavy Vehicle Use Tax)'),
        ('2290', 'Form 2290'),
        ('BOC-3', 'BOC-3 (Blanket of Coverage)'),
        ('MCS-150', 'MCS-150 (Motor Carrier Identification Report)'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Document Type'
    )
    deadline_date = models.DateField(verbose_name='Deadline Date')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    # Опциональные поля
    reminder_days = models.PositiveIntegerField(
        default=7,
        verbose_name='Reminder Days',
        help_text='Number of days before deadline to send reminder'
    )
    client_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Client Name',
        help_text='Optional: specific client for this deadline'
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        verbose_name = 'Deadline'
        verbose_name_plural = 'Deadlines'
        ordering = ['deadline_date', 'priority']
        indexes = [
            models.Index(fields=['deadline_date']),
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.deadline_date}"
    
    @property
    def is_overdue(self):
        """Проверка, просрочен ли дедлайн"""
        return self.deadline_date < timezone.now().date() and self.status != 'completed'
    
    @property
    def days_until_deadline(self):
        """Количество дней до дедлайна"""
        today = timezone.now().date()
        delta = self.deadline_date - today
        return delta.days
    
    @property
    def days_overdue(self):
        """Количество дней просрочки (только для просроченных)"""
        if self.days_until_deadline < 0:
            return abs(self.days_until_deadline)
        return 0
    
    @property
    def urgency_color(self):
        """Цвет для индикации срочности"""
        days = self.days_until_deadline
        if days < 0:
            return 'red'  # Просрочено
        elif days <= 7:
            return 'orange'  # Срочно
        elif days <= 30:
            return 'yellow'  # Скоро
        else:
            return 'green'  # В порядке
