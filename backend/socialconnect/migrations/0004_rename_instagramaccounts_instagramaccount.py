# Generated by Django 5.0.6 on 2024-05-31 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialconnect', '0003_instagramaccounts_delete_instagramaccount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InstagramAccounts',
            new_name='InstagramAccount',
        ),
    ]
