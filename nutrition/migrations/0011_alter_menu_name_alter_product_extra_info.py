# Generated by Django 4.0.1 on 2022-09-05 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0010_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='name',
            field=models.CharField(default='-', max_length=300),
        ),
        migrations.AlterField(
            model_name='product',
            name='extra_info',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
