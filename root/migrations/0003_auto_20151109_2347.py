# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0002_auto_20151109_2343'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrgEvent',
            new_name='Event',
        ),
    ]
