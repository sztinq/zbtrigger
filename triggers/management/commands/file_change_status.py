from django.core.management.base import BaseCommand, CommandError
from triggers.views import file_change_status
import time


class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray

    def handle(self, *args, **options):
        print "File Status Check Starting...."
        file_change_status(request=[])
        print "File Status Check access."

