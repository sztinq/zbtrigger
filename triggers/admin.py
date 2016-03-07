from django.contrib import admin
from triggers.models import Hosts, Parameters, TriggerWarrning, ZhuanXian, Video, History, Item, ItemLastValue, \
    InitPara, NetDevices, FtpServer, BackupHistory


# Register your models here.

class TriggerInline(admin.StackedInline):
    model = TriggerWarrning
    extra = 0


class HostsInline(admin.TabularInline):
    model = Hosts
    extra = 3


class HostsAdmin(admin.ModelAdmin):
    search_fields = ['hostip', 'hostname']
    list_display = ['company', 'hostname', 'hostip', 'status']
    fieldsets = [
        (None, {'fields': ['hostname']}),
        ('Device information', {'fields': ['company', 'hostid', 'hostip', 'status'], 'classes': ['collapse']}),
    ]
    # inlines = [TriggerInline]


class ParametersAdmin(admin.ModelAdmin):
    list_display = ['servername', 'serverip', 'user', 'password', 'authid']
    list_filter = ['serverip']
    search_fields = ['serverip']


class IniParaAdmin(admin.ModelAdmin):
    list_display = ['history_days', 'history_hours']


class ZhuanXianAdmin(admin.ModelAdmin):
    list_display = ['company', 'hostname', 'hostip']
    list_filter = ['hostip']
    search_fields = ['hostip']


class ViedoAdmin(admin.ModelAdmin):
    list_display = ['company', 'hostname', 'hostip']
    list_filter = ['hostip']
    search_fields = ['hostip']


class HistoryAdmin(admin.ModelAdmin):
    list_display = ['itemid', 'value', 'clock']
    list_filter = ['itemid']
    search_fields = ['itemid']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'hostip', 'itemid', 'itemkey', 'itemname', 'lastvalue', 'lastclock']
    list_filter = ['hostip']
    search_fields = ['hostip']


class ItemLastValueAdmin(admin.ModelAdmin):
    list_display = ['company', 'description', 'itemid', 'invalue', 'outvalue', 'clock']
    list_filter = ['itemid']
    search_fields = ['itemid']


class NetDevicesAdmin(admin.ModelAdmin):
    list_display = ['ipaddress', 'devicename', 'change_status', 'backup_status']
    list_filter = ['ipaddress']
    search_fields = ['ipaddress']


class BackupHistoryAdmin(admin.ModelAdmin):
    list_display = ['ipaddress', 'devicename', 'filename', 'contentchange']
    list_filter = ['ipaddress']
    search_fields = ['ipaddress']


class FtpServerAdmin(admin.ModelAdmin):
    list_display = ['ipaddress', 'username', 'password', 'filepath']


admin.site.register(Parameters, ParametersAdmin)
admin.site.register(InitPara, IniParaAdmin)
admin.site.register(Hosts, HostsAdmin)
admin.site.register(TriggerWarrning)
admin.site.register(ZhuanXian, ZhuanXianAdmin)
admin.site.register(Video, ViedoAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemLastValue, ItemLastValueAdmin)
admin.site.register(NetDevices, NetDevicesAdmin)
admin.site.register(BackupHistory, BackupHistoryAdmin)
admin.site.register(FtpServer, FtpServerAdmin)
