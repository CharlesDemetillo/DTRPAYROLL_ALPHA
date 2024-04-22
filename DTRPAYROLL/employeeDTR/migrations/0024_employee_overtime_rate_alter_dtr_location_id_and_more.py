# Generated by Django 5.0.3 on 2024-04-20 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employeeDTR', '0023_remove_employee_password_remove_employee_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='Overtime_rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='dtr',
            name='location_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='dtr',
            name='number',
            field=models.IntegerField(),
        ),
    ]
