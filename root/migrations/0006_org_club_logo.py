# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root', '0005_org_club_contact_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='club_logo',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
