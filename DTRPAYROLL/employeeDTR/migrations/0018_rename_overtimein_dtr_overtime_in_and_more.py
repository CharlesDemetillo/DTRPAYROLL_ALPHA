# Generated by Django 5.0.3 on 2024-03-25 01:52

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employeeDTR', '0017_employee_employee_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dtr',
            old_name='overtimeIn',
            new_name='overtime_in',
        ),
        migrations.RenameField(
            model_name='dtr',
            old_name='overtimeOut',
            new_name='overtime_out',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='date',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='timeIn_AM',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='timeIn_PM',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='timeOut_AM',
        ),
        migrations.RemoveField(
            model_name='dtr',
            name='timeOut_PM',
        ),
        migrations.AddField(
            model_name='dtr',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='dtr',
            name='department',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dtr',
            name='id_number',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dtr',
            name='location_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dtr',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dtr',
            name='number',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dtr',
            name='status',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
