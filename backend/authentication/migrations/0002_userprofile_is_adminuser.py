# Generated by Django 5.0.6 on 2024-06-06 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_adminuser',
            field=models.BooleanField(default=False, verbose_name='Adminuser status'),
        ),
    ]
