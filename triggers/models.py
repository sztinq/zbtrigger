# coding:utf-8
from django.db import models
from datetime import *
import time
import datetime


class Parameters(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    servername = models.CharField(max_length=200, default="北京总部")  # zabbix server name
    serverip = models.CharField(max_length=100, default="127.0.0.1")  # zabbix server ip
    url = models.CharField(max_length=300, default="http://127.0.0.1/zabbix/api_jsonrpc.php")  # zabbix server api url
    header_type = models.CharField(max_length=100, default="Content-Type")  # zabbix server url head
    header_json = models.CharField(max_length=100, default="application/json")
    method = models.CharField(max_length=100, default="user.login")  # zabbix server table
    user = models.CharField(max_length=100, default="Admin")  # zabbix server user
    password = models.CharField(max_length=100, default="zabbix")  # zabbix user password
    authid = models.CharField(max_length=100, default='0')  # zabbix server id

    def __unicode__(self):
        return self.serverip


class InitPara(models.Model):
    history_days = models.IntegerField(default=1)
    history_hours = models.IntegerField(default=1)


class Hosts(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    hostid = models.CharField(max_length=100)  # morned host
    hostip = models.CharField(max_length=100)  # morned IP
    hostname = models.CharField(max_length=300)  # morned name
    status = models.IntegerField(default=0)  # morned status

    def __unicode__(self):
        return self.hostname


class Triggers(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    hosts = models.ForeignKey(Hosts)
    triggerid = models.CharField(max_length=100)
    status = models.IntegerField()
    value = models.IntegerField()
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return self.triggerid


class TriggerWarrning(models.Model):
    hosts = models.ForeignKey(Hosts)
    company = models.CharField(max_length=100, default="北京总部")
    hostid = models.CharField(max_length=100, default="")
    hostname = models.CharField(max_length=300, default="")
    hostip = models.CharField(max_length=100, default="0")
    triggerid = models.CharField(max_length=100, default="")
    description = models.CharField(max_length=200, default="")
    lastchange = models.CharField(max_length=100, default="")

    def __unicode__(self):
        return self.hostname


class ZhuanXian(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    hostname = models.CharField(max_length=300, default="")
    hostip = models.CharField(max_length=300, default="")
    hostid = models.CharField(max_length=100, default="0", null=True)
    triggerid = models.CharField(max_length=100, default="0", null=True)
    description = models.CharField(max_length=200, default="0", null=True)
    lastchange = models.CharField(max_length=100, default="0", null=True)
    zhuanxianhao = models.CharField(max_length=100, default="0", null=True)
    manager = models.CharField(max_length=100, default="0", null=True)
    managerphone = models.CharField(max_length=100, default="0", null=True)
    yunyingshang = models.CharField(max_length=100, default="0", null=True)
    hotphone = models.CharField(max_length=100, default="0", null=True)

    def __unicode__(self):
        return self.hostname


class Video(models.Model):
    dcname = models.CharField(max_length=100, default="唐山数据中心")
    company = models.CharField(max_length=100, default="北京总部")
    hostname = models.CharField(max_length=300, default="")
    hostip = models.CharField(max_length=300, default="")
    hostid = models.CharField(max_length=100, default="0", null=True)
    triggerid = models.CharField(max_length=100, default="0", null=True)
    description = models.CharField(max_length=200, default="0", null=True)
    lastchange = models.CharField(max_length=100, default="0", null=True)
    manager = models.CharField(max_length=100, default="0", null=True)
    managerphone = models.CharField(max_length=100, default="0", null=True)

    def __unicode__(self):
        return self.hostname


class Item(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    hostname = models.CharField(max_length=300, default="")
    hostip = models.CharField(max_length=300, default="")
    hostid = models.CharField(max_length=100, default="0", null=True)
    itemid = models.CharField(max_length=100, default="0", null=True)
    itemkey = models.CharField(max_length=100, default="0", null=True)
    itemname = models.CharField(max_length=200, default="0", null=True)
    lastvalue = models.CharField(max_length=100, default="0", null=True)
    lastclock = models.CharField(max_length=100, default="0", null=True)
    description = models.CharField(max_length=200, default="0", null=True)

    def __unicode__(self):
        return self.hostname


class HistoryManager(models.Manager):
    def clear_history(self, keyword):
        # cursor = connections._databases
        # now = date.today()
        # last = now - now.replace(day)
        day_time = (date.today() - datetime.timedelta(days=keyword)).strftime('%Y-%m-%d %H:%M:%S')

        # return self.clock < day_time
        return self.filter(clock__icontains=keyword).count()


class History(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    itemid = models.CharField(max_length=100, default="0", null=True)
    value = models.CharField(max_length=100, default="0", null=True)
    clock = models.CharField(max_length=100, default="0", null=True)

    def __unicode__(self):
        return self.clock

    # class Meta:
    #    ordering = ['-clock']
    objects = models.Manager()
    history_objects = HistoryManager()


class ItemLastValue(models.Model):
    company = models.CharField(max_length=100, default="北京总部")
    itemid = models.CharField(max_length=100, default="0", null=True)
    invalue = models.CharField(max_length=100, default="0", null=True)
    outvalue = models.CharField(max_length=100, default="0", null=True)
    clock = models.CharField(max_length=100, default="0", null=True)
    description = models.CharField(max_length=200, default="0", null=True)

    def __unicode__(self):
        return self.itemid


class NetDevices(models.Model):
    ipaddress = models.CharField(max_length=100, default="10.1.0.11")
    devicename = models.CharField(max_length=100)
    description = models.CharField(max_length=100,default="ERP核心")
    type = models.CharField(max_length=100, default="cisco")
    tag = models.CharField(max_length=10, default="#")
    command = models.CharField(max_length=400, default="show running-config")
    username = models.CharField(max_length=100, default="dianjian")
    password = models.CharField(max_length=100, default="dianjian")
    change_status = models.IntegerField(default=0)
    backup_status = models.IntegerField(default=0)
    file_name = models.CharField(max_length=200, default="0")

    def __unicode__(self):
        return self.ipaddress


class FtpServer(models.Model):
    ipaddress = models.CharField(max_length=100, default="10.1.0.11")
    username = models.CharField(max_length=100, default="dianjian")
    password = models.CharField(max_length=100, default="dianjian")
    port = models.IntegerField(default=23)
    filepath = models.CharField(max_length=400)
    status = models.IntegerField(default=0)
    file_num = models.IntegerField(default=0)

    def __unicode__(self):
        return self.ipaddress


class BackupHistory(models.Model):
    ipaddress = models.CharField(max_length=100)
    devicename = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    contentchange = models.CharField(max_length=1000)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)

    def __unicode__(self):
        return self.ipaddress
