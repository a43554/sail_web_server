# Generated by Django 4.0.1 on 2022-06-12 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0006_alter_dish_options_remove_dish_validity_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='validity',
            new_name='auto_validity',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='weight_in_grams',
            new_name='ingredient_weight_in_grams',
        ),
        migrations.AddField(
            model_name='product',
            name='manual_validation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='non_ingredient_weight_in_grams',
            field=models.FloatField(default=0.0),
        ),
    ]
