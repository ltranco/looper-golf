# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0006_org_club_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='schedule',
            field=models.CharField(default='', max_length=100000),
            preserve_default=False,
        ),
    ]
