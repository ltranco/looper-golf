from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=10000)
    date = models.DateTimeField()
    organizer = models.CharField(max_length=255)

class Participation(models.Model):
    event = models.CharField(max_length=255)
    user = models.CharField(max_length=255)