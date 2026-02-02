# Generated manually - Initial migration for main app

from django.db import migrations, models


def create_initial_contacts(apps, schema_editor):
    """Создание начальных пустых контактов всех типов"""
    Contact = apps.get_model('main', 'Contact')
    
    contact_types = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
    ]
    
    for contact_type, _ in contact_types:
        Contact.objects.get_or_create(
            type=contact_type,
            defaults={
                'value': '',
            }
        )


def reverse_contacts(apps, schema_editor):
    """Откат - удаление всех контактов"""
    Contact = apps.get_model('main', 'Contact')
    Contact.objects.all().delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('meta_title', models.CharField(blank=True, help_text='Если не указан, используется заголовок страницы', max_length=255, verbose_name='Meta заголовок (SEO)')),
                ('meta_description', models.TextField(blank=True, max_length=500, verbose_name='Meta описание (SEO)')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубликовано')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Страница',
                'verbose_name_plural': 'Страницы',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('phone', 'Phone'), ('email', 'Email'), ('telegram', 'Telegram'), ('instagram', 'Instagram'), ('whatsapp', 'WhatsApp'), ('facebook', 'Facebook'), ('linkedin', 'LinkedIn')], max_length=20, verbose_name='Contact Type')),
                ('value', models.CharField(max_length=255, verbose_name='Value')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ['type'],
                'constraints': [
                    models.UniqueConstraint(fields=['type'], name='unique_contact_type'),
                ],
            },
        ),
        migrations.RunPython(
            code=create_initial_contacts,
            reverse_code=reverse_contacts,
        ),
    ]

