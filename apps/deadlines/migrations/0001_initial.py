# Generated manually - Initial migration for deadlines app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deadline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('document_type', models.CharField(choices=[('IFTA', 'IFTA (International Fuel Tax Agreement)'), ('IRP', 'IRP (International Registration Plan)'), ('UCR', 'UCR (Unified Carrier Registration)'), ('FMCSA', 'FMCSA (Federal Motor Carrier Safety Administration)'), ('DOT', 'DOT (Department of Transportation)'), ('HVUT', 'HVUT (Heavy Vehicle Use Tax)'), ('2290', 'Form 2290'), ('BOC-3', 'BOC-3 (Blanket of Coverage)'), ('MCS-150', 'MCS-150 (Motor Carrier Identification Report)'), ('other', 'Other')], max_length=20, verbose_name='Document Type')),
                ('deadline_date', models.DateField(verbose_name='Deadline Date')),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10, verbose_name='Priority')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('overdue', 'Overdue')], default='pending', max_length=20, verbose_name='Status')),
                ('reminder_days', models.PositiveIntegerField(default=7, help_text='Number of days before deadline to send reminder', verbose_name='Reminder Days')),
                ('client_name', models.CharField(blank=True, help_text='Optional: specific client for this deadline', max_length=255, verbose_name='Client Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Deadline',
                'verbose_name_plural': 'Deadlines',
                'ordering': ['deadline_date', 'priority'],
                'indexes': [
                    models.Index(fields=['deadline_date'], name='deadlines_d_deadlin_56d1b1_idx'),
                    models.Index(fields=['document_type'], name='deadlines_d_documen_3c3503_idx'),
                    models.Index(fields=['status'], name='deadlines_d_status_58631e_idx'),
                ],
            },
        ),
    ]

