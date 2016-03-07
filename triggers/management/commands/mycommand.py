from django.core.management.base import BaseCommand, CommandError
from triggers.views import trigger_thread

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Trigger_thread Starting...."
        trigger_thread(request=[])
        print "Trigger_thread access."