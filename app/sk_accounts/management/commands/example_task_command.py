from django.core.management.base import BaseCommand, CommandError
from sk_accounts.tasks import example_task

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        run this command and you will see activity in the rabbitmq admin interface at http://localhost:15672/
        the delay method will basically send a message to the rabbitmq queue so that the task will be run by the celery workers.
        celery workers are running in the "workers" service, so it should be running
        rabbitmq is running in the "rabbit" service, so it should be running
        """
        for item in range(1000):

            example_task.delay()
