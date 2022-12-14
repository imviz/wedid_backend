# Generated by Django 4.1 on 2022-09-27 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_product', models.CharField(max_length=100)),
                ('order_amount', models.CharField(max_length=25)),
                ('order_payment_id', models.CharField(max_length=100)),
                ('isPaid', models.BooleanField(default=False)),
                ('order_date', models.DateTimeField(auto_now=True)),
                ('buyer', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='buyer',
            field=models.BooleanField(default=False),
        ),
    ]
