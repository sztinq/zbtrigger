# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('triggers', '0004_ftpserver_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='ftpserver',
            name='file_num',
            field=models.IntegerField(default=0),
        ),
    ]
