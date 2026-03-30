from django.db import models


class Service(models.Model):
    """Service model"""
    title = models.CharField(max_length=255, verbose_name='Title')
    title_ru = models.CharField(max_length=255, blank=True, default='', verbose_name='Title (RU)')
    description = models.TextField(verbose_name='Description')
    description_ru = models.TextField(blank=True, default='', verbose_name='Description (RU)')
    image = models.ImageField(upload_to='services/', verbose_name='Image', blank=True, null=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['title']
    
    def __str__(self):
        return self.title
