# Generated by Django 4.0.1 on 2022-09-07 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_plan_sharing_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='plan_completion',
            field=models.BooleanField(default=False),
        ),
    ]
