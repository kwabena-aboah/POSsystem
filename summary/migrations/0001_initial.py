# Generated by Django 3.1.1 on 2020-12-18 12:31

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItemSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Product Report',
                'verbose_name_plural': 'Product Reports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('catalog.order_item',),
        ),
        migrations.CreateModel(
            name='OrderSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Order Report',
                'verbose_name_plural': 'Order Reports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('catalog.order',),
        ),
    ]