# Generated by Django 5.1.4 on 2024-12-25 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0002_auto_20241225_1107'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='reservation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
