from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from root.models import Event, Participation
import datetime, time

class IndexView(View):
    def get(self, request):
        print request.user
        events = Event.objects.all()
        context = {
            "events":events
        }

        return render(request, "index.html", context)

class EventView(View):
    def get(self, request, event_id):
        event = Event.objects.filter(id=event_id)[0]
        context = {
            "event_id":event_id,
            "event_name":event.name,
            "event_desc":event.description,
            "event_date":event.date,
            "event_loc":event.location,
        }

        if request.user.is_anonymous():
            return render(request, "event.html", context)

        participants = Participation.objects.filter(event=event_id)
        registered_participants = []
        
        for p in participants:
            registered = User.objects.filter(id=p.user)
            if registered:
                registered_participants.append(registered[0])

        print registered_participants

        context["participants"] = registered_participants
        return render(request, "event.html", context)

class RegisterView(View):
    def get(self, request, event_id):
        try:
            event = Event.objects.filter(id=event_id)[0]
            context = {
                "event_name":event.name
            }

            if Participation.objects.filter(event=event_id, user=request.user.id):
                return render(request, "success.html")
            par = Participation()
            par.event = event_id
            par.user = request.user.id
            par.save()
            
            return render(request, "success.html", context)
        except Exception as e:
            print e
            return redirect("/login")

class CreateView(View):
    def get(self, request):
        if request.user.is_anonymous():
            return redirect("/login")    
        
        return render(request, "create.html")

    def post(self, request):
        try:
            event = Event()
            event.name = request.POST.get("event_name")
            event.description = request.POST.get("event_desc")
            event.location = request.POST.get("event_loc")
            event.date = request.POST.get("event_date")
            event.organizer = request.user.id
            event.save()

            return render(request, "create.html", {"created":True})
        except Exception as e:
            print e
            return render(request, "create.html", {"failed":True})

class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        user = authenticate(username=request.POST.get("username"), 
                            password=request.POST.get("password"))
        
        if user is not None:
            login(request, user)
            return redirect("/")

        context = {
            "status":"The username and password were incorrect."
        }
        return render(request, "login.html", context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")

class SignUpView(View):
    def get(self, request):
        return render(request, "signup.html")
    
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.create_user(username, email, password)
            authenticated_user = authenticate(username=username, password=password)
            login(request, authenticated_user)
            return redirect("/")
        except Exception as e:
            print e
            return render(request, "signup.html", {"error": e})