from django.core.management.base import BaseCommand, CommandError
from triggers.views import host_thread
import time
class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray
    def handle(self, *args, **options):
        print "Host syn Starting...."
        host_thread(request=[])
        print "Host syn access."