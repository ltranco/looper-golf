# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0008_eventrecord'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventrecord',
            old_name='tee_time',
            new_name='tee',
        ),
    ]
