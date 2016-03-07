from django.core.management.base import BaseCommand, CommandError
from triggers.views import backup_netdevice
import time


class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray

    def handle(self, *args, **options):
        print "Backup Net Devices Starting...."
        backup_netdevice(request=[])
        print "Backup Net Devices access."
