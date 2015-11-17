# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0004_auto_20151117_0151'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='club_contact_person',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
