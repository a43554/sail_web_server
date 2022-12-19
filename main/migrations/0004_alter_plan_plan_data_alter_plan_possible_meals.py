# Generated by Django 4.0.1 on 2022-07-13 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0009_dish_description'),
        ('main', '0003_alter_plan_plan_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='plan_data',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='possible_meals',
            field=models.ManyToManyField(null=True, to='nutrition.Dish'),
        ),
    ]
