# Generated by Django 4.1 on 2022-09-30 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentportal', '0008_rent_detail_returned'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rent_detail',
            name='slug',
        ),
    ]