# Generated by Django 4.0.1 on 2022-04-22 10:30

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_alter_client_managers'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='client',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
