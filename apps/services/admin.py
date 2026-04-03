from django.contrib import admin
from django.contrib import messages
from .models import Service
from .translation import translate_en_to_ru


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ru', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = ["auto_translate_ru"]
    change_list_template = 'admin/services/service/change_list.html'

    @admin.action(description="Auto-translate EN → RU (fills empty RU fields)")
    def auto_translate_ru(self, request, queryset):
        updated = 0
        skipped = 0
        failed = 0
        last_error = None

        for service in queryset:
            changed = False

            if not (service.title_ru or "").strip() and (service.title or "").strip():
                r = translate_en_to_ru(service.title)
                if r.ok:
                    service.title_ru = r.text
                    changed = True
                else:
                    failed += 1
                    last_error = r.error
                    continue

            if not (service.description_ru or "").strip() and (service.description or "").strip():
                r = translate_en_to_ru(service.description)
                if r.ok:
                    service.description_ru = r.text
                    changed = True
                else:
                    failed += 1
                    last_error = r.error
                    continue

            if changed:
                service.save(update_fields=["title_ru", "description_ru", "updated_at"])
                updated += 1
            else:
                skipped += 1

        if updated:
            self.message_user(request, f"Translated and saved: {updated}", level=messages.SUCCESS)
        if skipped:
            self.message_user(request, f"Skipped (already had RU or empty EN): {skipped}", level=messages.INFO)
        if failed:
            msg = f"Failed: {failed}"
            if last_error:
                msg += f" (last error: {last_error})"
            self.message_user(request, msg, level=messages.ERROR)

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
