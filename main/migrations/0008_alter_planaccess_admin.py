# Generated by Django 4.0.1 on 2022-07-17 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_planaccess_plan_assigned_users_planaccess_plan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planaccess',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]