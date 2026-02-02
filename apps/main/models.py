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


class Contact(models.Model):
    """Contact information model"""
    TYPE_CHOICES = [
        ('phone', 'Phone'),
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
        verbose_name='Contact Type'
    )
    value = models.CharField(max_length=255, verbose_name='Value', blank=True, null=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['type']
        constraints = [
            models.UniqueConstraint(fields=['type'], name='unique_contact_type')
        ]
    
    def __str__(self):
        value_display = self.value if self.value else "(empty)"
        return f"{self.get_type_display()}: {value_display}"
