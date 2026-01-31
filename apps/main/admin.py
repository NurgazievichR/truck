from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Page, Advantage, Contact


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'edit_button']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    list_display_links = None  # Убрать кликабельность строк
    
    fieldsets = (
        ('Содержание страницы', {
            'fields': ('title', 'content'),
            'description': 'Заполните заголовок и текст страницы. URL страницы формируется автоматически.'
        }),
    )
    
    def edit_button(self, obj):
        """Кнопка для редактирования страницы"""
        url = reverse('admin:main_page_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Редактировать</a>', url)
    
    edit_button.short_description = 'Действия'
    
    def has_add_permission(self, request):
        """Запретить создание новых страниц"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление страниц"""
        return False


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Настройки отображения', {
            'fields': ('order', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['get_type_display', 'value', 'is_active']
    list_editable = ['value', 'is_active']
    readonly_fields = ['type', 'order', 'created_at', 'updated_at']
    list_display_links = None  # Убрать кликабельность строк
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('type', 'value')
        }),
        ('Настройки отображения', {
            'fields': ('order', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Редирект на changelist если кто-то попытается открыть detail view"""
        from django.shortcuts import redirect
        return redirect('admin:main_contact_changelist')
    
    def has_add_permission(self, request):
        """Запретить создание новых контактов"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление контактов"""
        return False
    
    def has_view_permission(self, request, obj=None):
        """Запретить просмотр детальной страницы"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Разрешить изменение только через list_editable"""
        return True
