# Generated by Django 4.0.1 on 2022-05-29 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0003_dish_validity'),
    ]

    operations = [
        migrations.AddField(
            model_name='dishingredient',
            name='validity',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
