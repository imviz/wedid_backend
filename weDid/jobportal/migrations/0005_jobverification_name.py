# Generated by Django 4.1 on 2022-09-27 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobportal', '0004_jobverification_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobverification',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
