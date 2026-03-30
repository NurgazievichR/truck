from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ru', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = None  # Remove actions
    change_list_template = 'admin/services/service/change_list.html'
    
    def get_actions(self, request):
        """Remove actions completely"""
        actions = super().get_actions(request)
        return {}
    
    fieldsets = (
        ('Main Information (EN)', {
            'fields': ('title', 'description')
        }),
        ('Main Information (RU)', {
            'fields': ('title_ru', 'description_ru')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
