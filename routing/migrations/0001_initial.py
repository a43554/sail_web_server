# Generated by Django 4.0.1 on 2022-07-30 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_start_date', models.DateTimeField()),
                ('expected_end_date', models.DateTimeField()),
                ('end_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_ends', to='routing.location')),
                ('start_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_starts', to='routing.location')),
            ],
        ),
        migrations.CreateModel(
            name='StopLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='routing.location')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='routing.route')),
            ],
            options={
                'unique_together': {('route', 'location', 'order')},
            },
        ),
        migrations.AddField(
            model_name='route',
            name='stop_locations',
            field=models.ManyToManyField(blank=True, related_name='route_stops', through='routing.StopLocation', to='routing.Location'),
        ),
    ]