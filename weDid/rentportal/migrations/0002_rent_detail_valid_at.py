# Generated by Django 4.1 on 2022-09-12 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentportal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent_detail',
            name='valid_at',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]