# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-23 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0004_auto_20181023_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('meeting_notes', models.CharField(max_length=512)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.Participant')),
            ],
        ),
    ]
