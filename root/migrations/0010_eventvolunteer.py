# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0009_auto_20151125_0841'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventVolunteer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('email', models.CharField(max_length=500)),
                ('role', models.CharField(max_length=500)),
                ('event', models.ForeignKey(blank=True, to='root.Event', null=True)),
            ],
        ),
    ]
