# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class TriggersHistory(models.Model):
    itemid = models.CharField(max_length=100, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True, null=True)
    clock = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'triggers_history'


class TriggersHosts(models.Model):
    company = models.CharField(max_length=100)
    hostid = models.CharField(max_length=100)
    hostip = models.CharField(max_length=100)
    hostname = models.CharField(max_length=300)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'triggers_hosts'


class TriggersItem(models.Model):
    company = models.CharField(max_length=100)
    hostname = models.CharField(max_length=300)
    hostip = models.CharField(max_length=300)
    hostid = models.CharField(max_length=100, blank=True, null=True)
    itemid = models.CharField(max_length=100, blank=True, null=True)
    itemkey = models.CharField(max_length=100, blank=True, null=True)
    itemname = models.CharField(max_length=200, blank=True, null=True)
    lastclock = models.CharField(max_length=100, blank=True, null=True)
    lastvalue = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'triggers_item'


class TriggersItemlastvalue(models.Model):
    itemid = models.CharField(max_length=100, blank=True, null=True)
    invalue = models.CharField(max_length=100, blank=True, null=True)
    clock = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=100)
    outvalue = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'triggers_itemlastvalue'


class TriggersParameters(models.Model):
    company = models.CharField(max_length=100)
    servername = models.CharField(max_length=200)
    serverip = models.CharField(max_length=100)
    url = models.CharField(max_length=300)
    header_type = models.CharField(max_length=100)
    header_json = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    authid = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'triggers_parameters'


class TriggersTriggers(models.Model):
    company = models.CharField(max_length=100)
    triggerid = models.CharField(max_length=100)
    status = models.IntegerField()
    value = models.IntegerField()
    description = models.CharField(max_length=200)
    hosts = models.ForeignKey(TriggersHosts)

    class Meta:
        managed = False
        db_table = 'triggers_triggers'


class TriggersTriggerwarrning(models.Model):
    company = models.CharField(max_length=100)
    hostid = models.CharField(max_length=100)
    hostname = models.CharField(max_length=300)
    hostip = models.CharField(max_length=100)
    triggerid = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    lastchange = models.CharField(max_length=100)
    hosts = models.ForeignKey(TriggersHosts)

    class Meta:
        managed = False
        db_table = 'triggers_triggerwarrning'


class TriggersVideo(models.Model):
    dcname = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    hostname = models.CharField(max_length=300)
    hostip = models.CharField(max_length=300)
    hostid = models.CharField(max_length=100, blank=True, null=True)
    triggerid = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    lastchange = models.CharField(max_length=100, blank=True, null=True)
    manager = models.CharField(max_length=100, blank=True, null=True)
    managerphone = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'triggers_video'


class TriggersZhuanxian(models.Model):
    company = models.CharField(max_length=100)
    hostname = models.CharField(max_length=300)
    hostip = models.CharField(max_length=300)
    hostid = models.CharField(max_length=100, blank=True, null=True)
    triggerid = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    lastchange = models.CharField(max_length=100, blank=True, null=True)
    zhuanxianhao = models.CharField(max_length=100, blank=True, null=True)
    manager = models.CharField(max_length=100, blank=True, null=True)
    managerphone = models.CharField(max_length=100, blank=True, null=True)
    yunyingshang = models.CharField(max_length=100, blank=True, null=True)
    hotphone = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'triggers_zhuanxian'
