# Generated by Django 4.2.16 on 2024-11-11 08:10

import adjango.managers.base
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='products',
            field=adjango.fields.AManyToManyField(to='app.product'),
        ),
    ]