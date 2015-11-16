from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from root.models import Event, Participation, Org
import datetime, time

class IndexView(View):
    def get(self, request):
        events = Event.objects.filter(private=False)
        context = {
            "events":events
        }

        if not request.user.is_anonymous():
            url = "/clubs/" if Org.objects.filter(user=request.user) else "/users/"
            context["dashboard_url"] = url + request.user.username

        return render(request, "index.html", context)

class EventView(View):
    def get(self, request, org_id, event_id):
        event = Event.objects.filter(id=event_id)[0]
        context = {
            "event_id":event_id,
            "event_name":event.name,
            "event_desc":event.description,
            "event_date":event.date,
            "event_loc":event.location,
            "org_status":request.user.username == org_id,
            "org_id":org_id,
            "unregister":False
        }

        if request.user.is_anonymous():
            return render(request, "event.html", context)
        elif Participation.objects.filter(event=event_id, user=request.user):
            context["unregister"] = True

        participants = Participation.objects.filter(event=event_id)
        registered_participants = []
        
        for p in participants:
            registered = User.objects.get(username=p.user.username)
            if registered:
                registered_participants.append(registered)

        context["participants"] = registered_participants
        return render(request, "event.html", context)

class RegisterView(View):
    def get(self, request, org_id, event_id):
        try:
            if request.user.username == org_id:
                return redirect("/clubs/" + org_id)

            if Participation.objects.filter(event=event_id, user=request.user):
                return redirect("/clubs/" + org_id + "/events/" + event_id)

            par = Participation()
            par.event = Event.objects.get(id=event_id)
            par.user = request.user
            par.save()
            
            return redirect("/clubs/" + org_id + "/events/" + event_id)
        except Exception as e:
            print e
            return redirect("/login")

class CreateView(View):
    def get(self, request, org_id):
        if request.user.is_anonymous() or request.user.username != org_id:
            return redirect("/")
        return render(request, "create.html")

    def post(self, request, org_id):
        if request.user.is_anonymous() or request.user.username != org_id:
            return redirect("/")
        try:
            event = Event()
            event.name = request.POST.get("event_name")
            event.description = request.POST.get("event_desc")
            event.location = request.POST.get("event_loc")
            event.date = request.POST.get("event_date")
            event.private = True if request.POST.get("event_private") == "Yes" else False
            event.organizer = request.user
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
            org = Org.objects.filter(user=request.user)
            if org:
                return redirect("/clubs/" + str(org[0].user.username))
            return redirect("/")

        context = {
            "status":"The username and password were incorrect."
        }
        return render(request, "login.html", context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")

class UnregisterView(View):
    def get(self, request, org_id, event_id):
        try:
            Participation.objects.filter(user=request.user, event=event_id).delete()
        except Exception as e:
            print e
        return redirect("/clubs/" + org_id + "/events/" + event_id)


class OrgView(View):
    def get(self, request, org_id):
        user = User.objects.get(username=org_id)
        org = Org.objects.filter(user=user)
        org = org[0] if org else org

        events = Event.objects.filter(organizer=user)
        context = {
            "club_name":org.club_name,
            "club_address":org.club_address,
            "club_phone":org.club_phone,
            "club_organizer":org.user.first_name + " " + org.user.last_name,
            "org_status":True,
            "events":events
        }
        if request.user.username != org_id:
            context["org_status"] = False
            
        return render(request, "org.html", context)

class OrgDeleteView(View):
    def get(self, request, org_id, event_id):
        if request.user.username != org_id:
            return redirect("/clubs/" + org_id)
        try:
            Event.objects.filter(id=event_id, organizer=request.user).delete()
        except Exception as e:
            print e
        return redirect("/clubs/" + org_id)

class OrgEditView(View):
    def get(self, request, org_id, event_id):
        if request.user.username != org_id:
            return redirect("/")
        event = Event.objects.filter(id=event_id)[0]
        context = {
            "event":event,
            "event_date":str(event.date).replace(" ", "T")[:16]
        }
        return render(request, "orgedit.html", context)

    def post(self, request, org_id, event_id):
        if request.user.username != org_id:
            return redirect("/")

        event_name = request.POST.get("event_name")
        event_desc = request.POST.get("event_desc")
        event_loc = request.POST.get("event_loc")
        event_date = request.POST.get("event_date")
        event_private = request.POST.get("event_private")

        context = {
            "changed":True
        }
        try:
            event = Event.objects.filter(id=event_id)[0]

            context["event"] = event
            context["event_date"] = str(event.date).replace(" ", "T")[:16]
            if event_name:
                event.name = event_name
            if event_desc:
                event.description = event_desc
            if event_loc:
                event.location = event_loc
            if event_date:
                event.date = event_date
            if event_private:
                event.private = True if event_private == "Yes" else False
            event.save()

            return render(request, "orgedit.html", context)
        except Exception as e:
            print e
            context["changed"] = False
            context["failed"] = True
            return render(request, "orgedit.html", context)

class SignUpView(View):
    def get(self, request):
        return render(request, "signup.html")
    
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        full_name = request.POST.get("full-name")
        first_name, last_name = full_name.split() if " " in full_name else ("", "")

        if not (username and email and password and confirm_password):
            return render(request, "signup.html", {"error": "Please fill in all required fields."})
        elif password != confirm_password:
            return render(request, "signup.html", {"error": "Password does not match."})

        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            authenticated_user = authenticate(username=username, password=password)
            login(request, authenticated_user)
            return redirect("/")
        except Exception as e:
            print e
            return render(request, "signup.html", {"error": "This username is already taken."})

class OrgSignUpView(View):
    def get(self, request):
        return render(request, "orgsignup.html")

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        full_name = request.POST.get("full-name")
        first_name, last_name = full_name.split() if " " in full_name else ("", "")
        club_name = request.POST.get("club-name")
        club_address = request.POST.get("club-address")
        club_phone = request.POST.get("club-phone")

        if not (username and email and password and confirm_password and club_name and full_name):
            return render(request, "orgsignup.html", {"error": "Please fill in all required fields."})
        elif password != confirm_password:
            return render(request, "orgsignup.html", {"error": "Password does not match."})

        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.is_staff = True
            authenticated_user = authenticate(username=username, password=password)
            org = Org()
            org.user = user
            org.club_address = club_address
            org.club_phone = club_phone
            org.club_name = club_name
            org.save()
            login(request, authenticated_user)
            return redirect("/")
        except Exception as e:
            print e
            return render(request, "orgsignup.html", {"error": "This username is already taken."})

