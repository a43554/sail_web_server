# Generated by Django 4.0.1 on 2022-10-10 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0011_alter_menu_name_alter_product_extra_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='product_priority',
            field=models.CharField(default='NONE', max_length=100),
        ),
    ]