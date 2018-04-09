# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import task
import time


@task(queue='default')
def example_task():
    print("this task can be called anywhere by importing and calling example_task.dela()")

@task(queue='beat')
def example_beat_task():
    """
    beat tasks are scheduled in app.settings.CELERY_BEAT_SCHEDULE
    """
    print("Task is scheduled using celery beat")
