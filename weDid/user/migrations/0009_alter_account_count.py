# Generated by Django 4.1 on 2022-08-28 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_alter_account_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]