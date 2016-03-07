# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackupHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ipaddress', models.CharField(max_length=100)),
                ('devicename', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=100)),
                ('contentchange', models.CharField(max_length=1000)),
                ('date', models.CharField(max_length=100)),
                ('time', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FtpServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ipaddress', models.CharField(default=b'10.1.0.11', max_length=100)),
                ('username', models.CharField(default=b'dianjian', max_length=100)),
                ('password', models.CharField(default=b'dianjian', max_length=100)),
                ('port', models.IntegerField(default=23)),
                ('filepath', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('itemid', models.CharField(default=b'0', max_length=100, null=True)),
                ('value', models.CharField(default=b'0', max_length=100, null=True)),
                ('clock', models.CharField(default=b'0', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hosts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('hostid', models.CharField(max_length=100)),
                ('hostip', models.CharField(max_length=100)),
                ('hostname', models.CharField(max_length=300)),
                ('status', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='InitPara',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('history_days', models.IntegerField(default=1)),
                ('history_hours', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('hostname', models.CharField(default=b'', max_length=300)),
                ('hostip', models.CharField(default=b'', max_length=300)),
                ('hostid', models.CharField(default=b'0', max_length=100, null=True)),
                ('itemid', models.CharField(default=b'0', max_length=100, null=True)),
                ('itemkey', models.CharField(default=b'0', max_length=100, null=True)),
                ('itemname', models.CharField(default=b'0', max_length=200, null=True)),
                ('lastvalue', models.CharField(default=b'0', max_length=100, null=True)),
                ('lastclock', models.CharField(default=b'0', max_length=100, null=True)),
                ('description', models.CharField(default=b'0', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemLastValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('itemid', models.CharField(default=b'0', max_length=100, null=True)),
                ('invalue', models.CharField(default=b'0', max_length=100, null=True)),
                ('outvalue', models.CharField(default=b'0', max_length=100, null=True)),
                ('clock', models.CharField(default=b'0', max_length=100, null=True)),
                ('description', models.CharField(default=b'0', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NetDevices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ipaddress', models.CharField(default=b'10.1.0.11', max_length=100)),
                ('devicename', models.CharField(max_length=100)),
                ('description', models.CharField(default=b'ERP\xe6\xa0\xb8\xe5\xbf\x83', max_length=100)),
                ('type', models.CharField(default=b'cisco', max_length=100)),
                ('tag', models.CharField(default=b'#', max_length=10)),
                ('command', models.CharField(default=b'copy running-config ftp://', max_length=400)),
                ('username', models.CharField(default=b'dianjian', max_length=100)),
                ('password', models.CharField(default=b'dianjian', max_length=100)),
                ('status', models.IntegerField(default=0)),
                ('success', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('servername', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=200)),
                ('serverip', models.CharField(default=b'127.0.0.1', max_length=100)),
                ('url', models.CharField(default=b'http://127.0.0.1/zabbix/api_jsonrpc.php', max_length=300)),
                ('header_type', models.CharField(default=b'Content-Type', max_length=100)),
                ('header_json', models.CharField(default=b'application/json', max_length=100)),
                ('method', models.CharField(default=b'user.login', max_length=100)),
                ('user', models.CharField(default=b'Admin', max_length=100)),
                ('password', models.CharField(default=b'zabbix', max_length=100)),
                ('authid', models.CharField(default=b'0', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Triggers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('triggerid', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('value', models.IntegerField()),
                ('description', models.CharField(max_length=200)),
                ('hosts', models.ForeignKey(to='triggers.Hosts')),
            ],
        ),
        migrations.CreateModel(
            name='TriggerWarrning',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('hostid', models.CharField(default=b'', max_length=100)),
                ('hostname', models.CharField(default=b'', max_length=300)),
                ('hostip', models.CharField(default=b'0', max_length=100)),
                ('triggerid', models.CharField(default=b'', max_length=100)),
                ('description', models.CharField(default=b'', max_length=200)),
                ('lastchange', models.CharField(default=b'', max_length=100)),
                ('hosts', models.ForeignKey(to='triggers.Hosts')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dcname', models.CharField(default=b'\xe5\x94\x90\xe5\xb1\xb1\xe6\x95\xb0\xe6\x8d\xae\xe4\xb8\xad\xe5\xbf\x83', max_length=100)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('hostname', models.CharField(default=b'', max_length=300)),
                ('hostip', models.CharField(default=b'', max_length=300)),
                ('hostid', models.CharField(default=b'0', max_length=100, null=True)),
                ('triggerid', models.CharField(default=b'0', max_length=100, null=True)),
                ('description', models.CharField(default=b'0', max_length=200, null=True)),
                ('lastchange', models.CharField(default=b'0', max_length=100, null=True)),
                ('manager', models.CharField(default=b'0', max_length=100, null=True)),
                ('managerphone', models.CharField(default=b'0', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ZhuanXian',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'\xe5\x8c\x97\xe4\xba\xac\xe6\x80\xbb\xe9\x83\xa8', max_length=100)),
                ('hostname', models.CharField(default=b'', max_length=300)),
                ('hostip', models.CharField(default=b'', max_length=300)),
                ('hostid', models.CharField(default=b'0', max_length=100, null=True)),
                ('triggerid', models.CharField(default=b'0', max_length=100, null=True)),
                ('description', models.CharField(default=b'0', max_length=200, null=True)),
                ('lastchange', models.CharField(default=b'0', max_length=100, null=True)),
                ('zhuanxianhao', models.CharField(default=b'0', max_length=100, null=True)),
                ('manager', models.CharField(default=b'0', max_length=100, null=True)),
                ('managerphone', models.CharField(default=b'0', max_length=100, null=True)),
                ('yunyingshang', models.CharField(default=b'0', max_length=100, null=True)),
                ('hotphone', models.CharField(default=b'0', max_length=100, null=True)),
            ],
        ),
    ]
