from django.core.management.base import BaseCommand, CommandError
from triggers.views import trigger_thread
import time


class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray

    def handle(self, *args, **options):
        print "Trigger syn Starting...."
        trigger_thread(request=[])
        print "Trigger syn access."
