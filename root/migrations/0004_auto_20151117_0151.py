# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0003_playerorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerorder',
            name='event',
        ),
        migrations.RemoveField(
            model_name='playerorder',
            name='player',
        ),
        migrations.AddField(
            model_name='participation',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PlayerOrder',
        ),
    ]
