# Generated by Django 4.0.1 on 2022-06-05 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0004_dishingredient_validity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dishingredient',
            name='dish',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.dish'),
        ),
        migrations.AlterField(
            model_name='dishingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.ingredient'),
        ),
        migrations.AlterField(
            model_name='product',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.ingredient'),
        ),
    ]
