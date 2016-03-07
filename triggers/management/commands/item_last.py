from django.core.management.base import BaseCommand, CommandError
from triggers.views import item_last
import time


class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray

    def handle(self, *args, **options):
        print "Item last value syn Starting...."
        item_last(request=[])
        print "Item last value syn access."
