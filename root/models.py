from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=10000)
    date = models.DateTimeField()
    organizer = models.ForeignKey(User, null=True, blank=True)
    private = models.BooleanField(default=False)

class Participation(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    order = models.IntegerField()

class Org(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    club_name = models.CharField(max_length=500)
    club_address = models.CharField(max_length=500)
    club_phone = models.CharField(max_length=500)
    club_contact_person = models.CharField(null=True, max_length=500, blank=True)
