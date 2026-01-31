from django.db import models
from django.utils.text import slugify


class Page(models.Model):
    """Модель для статических страниц (О компании, Как мы работаем)"""
    slug = models.SlugField(unique=True, max_length=100, verbose_name='URL')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    
    # SEO поля
    meta_title = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Meta заголовок (SEO)',
        help_text='Если не указан, используется заголовок страницы'
    )
    meta_description = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='Meta описание (SEO)'
    )
    
    # Статус
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Advantage(models.Model):
    """Модель для преимуществ компании"""
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Иконка',
        help_text='Название иконки (например: check, star, shield)'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class Contact(models.Model):
    """Модель для контактной информации"""
    TYPE_CHOICES = [
        ('phone', 'Телефон'),
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
    ]
    
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        verbose_name='Тип контакта'
    )
    value = models.CharField(max_length=255, verbose_name='Значение')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['order', 'type']
        constraints = [
            models.UniqueConstraint(fields=['type'], name='unique_contact_type')
        ]
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"
