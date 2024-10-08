# Generated by Django 5.0.6 on 2024-05-31 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialconnect', '0002_instagramaccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instagram_id', models.CharField(max_length=100)),
                ('instagram_username', models.CharField(max_length=100)),
                ('extra_data', models.JSONField()),
                ('facebook_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialconnect.facebookpage')),
            ],
        ),
        migrations.DeleteModel(
            name='InstagramAccount',
        ),
    ]
