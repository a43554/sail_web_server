# Generated by Django 4.0.1 on 2022-04-22 09:47

from django.db import migrations, models
import utils.new.ScheduleOptions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Handler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('display_name', models.CharField(max_length=150)),
                ('task_description', models.TextField(blank=True, max_length=500, null=True)),
                ('task_category', models.CharField(max_length=50)),
                ('task_sub_category', models.CharField(max_length=50)),
                ('advanced_settings', models.JSONField(default=utils.new.ScheduleOptions.ScheduleOptions.get_default_settings)),
                ('incompatible_person_tasks', models.ManyToManyField(blank=True, to='scheduling.Task')),
                ('qualified_handlers', models.ManyToManyField(blank=True, related_name='task_qualifications', to='scheduling.Handler')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('display_name', models.CharField(max_length=150)),
                ('total_shift_amount', models.IntegerField()),
                ('total_shifts_per_day', models.IntegerField(null=True)),
                ('last_solutions', models.JSONField(blank=True, default=dict, null=True)),
                ('handlers', models.ManyToManyField(related_name='schedules', to='scheduling.Handler')),
                ('tasks', models.ManyToManyField(related_name='schedules', to='scheduling.Task')),
            ],
        ),
    ]