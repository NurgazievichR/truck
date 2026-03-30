from django.db import migrations, models


def seed_ru_fields(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    mapping = (
        ('ifta', 'IFTA и топливный налог', 'Регистрация, квартальная отчетность и соблюдение требований по топливному налогу во всех юрисдикциях.'),
        ('irp', 'IRP и регистрация', 'Пропорциональная регистрация, продления и оформление прицепов для межштатных перевозок.'),
        ('ucr', 'UCR и разрешения', 'Unified Carrier Registration и разрешения штатов — без срывов и штрафов.'),
        ('fmcsa', 'FMCSA и безопасность', 'Соблюдение требований по безопасности, поддержка CSA и готовность к аудитам DOT.'),
    )
    for service in Service.objects.all():
        title_l = (service.title or '').lower()
        desc_l = (service.description or '').lower()
        for token, ru_title, ru_desc in mapping:
            if token in title_l or token in desc_l:
                if not (service.title_ru or '').strip():
                    service.title_ru = ru_title
                if not (service.description_ru or '').strip():
                    service.description_ru = ru_desc
                service.save(update_fields=['title_ru', 'description_ru'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='description_ru',
            field=models.TextField(blank=True, default='', verbose_name='Description (RU)'),
        ),
        migrations.AddField(
            model_name='service',
            name='title_ru',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Title (RU)'),
        ),
        migrations.RunPython(seed_ru_fields, migrations.RunPython.noop),
    ]
