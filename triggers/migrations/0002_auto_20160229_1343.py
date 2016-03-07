# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('triggers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='netdevices',
            old_name='status',
            new_name='backup_status',
        ),
        migrations.RenameField(
            model_name='netdevices',
            old_name='success',
            new_name='change_status',
        ),
        migrations.AlterField(
            model_name='netdevices',
            name='command',
            field=models.CharField(default=b'show running-config', max_length=400),
        ),
    ]
