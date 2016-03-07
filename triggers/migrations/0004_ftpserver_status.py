# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('triggers', '0003_netdevices_file_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ftpserver',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
