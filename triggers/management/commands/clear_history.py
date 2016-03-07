from django.core.management.base import BaseCommand, CommandError
from triggers.views import clear_history
import time


class Command(BaseCommand):
    timearray = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print timearray

    def handle(self, *args, **options):
        print "History data is cleaning...."
        try:
            clear_history(request=[])
        except CommandError, ex:
                print CommandError, ":", ex
        print "History data clear access."
