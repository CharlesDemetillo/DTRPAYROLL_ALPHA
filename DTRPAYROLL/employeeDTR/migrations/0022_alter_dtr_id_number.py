# Generated by Django 5.0.3 on 2024-03-25 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employeeDTR', '0021_alter_dtr_id_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dtr',
            name='id_number',
            field=models.IntegerField(null=True),
        ),
    ]
