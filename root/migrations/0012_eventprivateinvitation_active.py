# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0011_eventprivateinvitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventprivateinvitation',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
