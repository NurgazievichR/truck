from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Contact

# Unregister User and Group
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['get_type_display', 'value']
    list_editable = ['value']
    readonly_fields = ['type', 'created_at', 'updated_at']
    list_display_links = None  # Remove row clickability
    change_list_template = 'admin/main/contact/change_list.html'
    
    fieldsets = (
        ('Main Information', {
            'fields': ('type', 'value')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Redirect to changelist if someone tries to open detail view"""
        from django.shortcuts import redirect
        return redirect('admin:main_contact_changelist')
    
    def has_add_permission(self, request):
        """Disable creating new contacts"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting contacts"""
        return False
    
    def has_view_permission(self, request, obj=None):
        """Disable viewing detail page"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow editing only through list_editable"""
        return True
