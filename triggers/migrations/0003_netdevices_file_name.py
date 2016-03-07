# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('triggers', '0002_auto_20160229_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='netdevices',
            name='file_name',
            field=models.CharField(default=b'0', max_length=200),
        ),
    ]
