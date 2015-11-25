# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('root', '0007_event_schedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tee_time', models.CharField(max_length=500)),
                ('cart', models.CharField(max_length=500)),
                ('flight', models.CharField(max_length=500)),
                ('score', models.CharField(max_length=500)),
                ('event', models.ForeignKey(blank=True, to='root.Event', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
