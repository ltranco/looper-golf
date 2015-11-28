from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=10000)
    date = models.DateTimeField()
    organizer = models.ForeignKey(User, null=True, blank=True)
    schedule = models.CharField(max_length=100000)
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
    club_logo = models.CharField(null=True, max_length=500, blank=True)

class EventRecord(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    tee = models.CharField(max_length=500)
    cart = models.CharField(max_length=500)
    flight = models.CharField(max_length=500)
    score = models.CharField(max_length=500)

class EventVolunteer(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    name = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
    role = models.CharField(max_length=500)

class EventPrivateInvitation(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    name = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
    key = models.CharField(max_length=500)
    invited = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class OrgAssistant(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    org = models.ForeignKey(User, null=True, blank=True, related_name='belong_to_org')