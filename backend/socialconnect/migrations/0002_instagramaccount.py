# Generated by Django 5.0.6 on 2024-05-31 13:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialconnect', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instagram_id', models.CharField(max_length=100)),
                ('instagram_username', models.CharField(max_length=100)),
                ('facebook_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialconnect.facebookpage')),
            ],
        ),
    ]
