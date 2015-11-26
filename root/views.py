from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from root.models import Event, Participation, Org, EventRecord, EventVolunteer, EventPrivateInvitation
from django.core.mail import send_mail
import datetime, time, os, threading

""" Splash View """
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

""" Signing Up Views """
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

""" Logging In and Out """
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

""" Organization Views """
class OrgView(View):
    def get_context(self, org_id):
        user = User.objects.get(username=org_id)
        org = Org.objects.filter(user=user)
        org = org[0] if org else org

        events = Event.objects.filter(organizer=user)
        all_participants = list(set([par for event in events for par in Participation.objects.filter(event=event)]))

        return {
            "club_name":org.club_name,
            "club_address":org.club_address,
            "club_phone":org.club_phone,
            "club_contact_person":org.club_contact_person,
            "club_logo":org.club_logo,
            "org_status":True,
            "events":events,
            "org_id":org_id,
            "org_object":org,
            "all_participants":all_participants
        }

    def change_logo(self, context, request, org_id):
        new_logo = request.FILES.get("uploaded_file", None)
        try:
            if new_logo.size > 5000000:
                context["oversize"] = True
                return render(request, "org.html", context)

            file_name = org_id + "_" + str(int(time.time())) + new_logo.name
            context["club_logo"] = file_name

            org = context["org_object"]
            if org.club_logo:
                try:
                    os.remove("root/static/img/logos/" + org.club_logo)
                except Exception as e:
                    print e
            org.club_logo = file_name
            org.save()

            file_path = "root/static/img/logos/" + file_name
            with open(file_path, 'wb+') as destination:
                for chunk in new_logo.chunks():
                    destination.write(chunk)
        except Exception as e:
            print e
        return render(request, "org.html", context)

    def blast_emails(self, context, request, org_id):
        util = Utility()
        emails = util.get_emails_from_events(context["events"])
        subject = request.POST.get("message_subject", "A Message from " + org_id)
        body = request.POST.get("message_body", "")
        html = True if request.POST.get("message_html") else False
        try:
            util.blast_emails(subject, body, emails, html=html)
            context["email_blast_success"] = True
        except Exception as e:
            print e
        return render(request, "org.html", context)

    def get(self, request, org_id):
        context = self.get_context(org_id)
        if request.user.username != org_id:
            context["org_status"] = False
        return render(request, "org.html", context)

    def post(self, request, org_id):
        context = self.get_context(org_id)

        if request.user.username != org_id:
            context["org_status"] = False

        if "change_logo" in request.POST:
            return self.change_logo(context, request, org_id)
        elif "blast_emails" in request.POST:
            return self.blast_emails(context, request, org_id)
        
class Utility():
    def get_emails_from_events(self, events):
        participations = [Participation.objects.filter(event=event.id) for event in events]
        return list(set([par.user.email for pars in participations for par in pars]))

    def blast_emails(self, subject, body, emails, html=False):
        send_email_thread = threading.Thread(target=self.threaded_send_email, args=(subject, body, emails, html))
        send_email_thread.start()

    def threaded_send_email(self, subject, body, emails, html=False):
        if html:
            for email in emails:
                send_mail(subject, "", 'LooperGolfLLC@gmail.com', [email], fail_silently=False, html_message=body)
        else:
            for email in emails:
                send_mail(subject, body, 'LooperGolfLLC@gmail.com', [email], fail_silently=False)

class OrgUpdateView(View):
    def get(self, request, org_id):
        if request.user.username != org_id:
            return redirect("/")

        org = Org.objects.filter(user=request.user)
        org = org[0] if org else org

        context = {
            "org_id":org_id,
            "org_name":org.club_name,
            "org_address":org.club_address,
            "org_phone":org.club_phone,
            "org_contact_person":org.club_contact_person,
            "dashboard_url":"/clubs/" + org_id
        }

        return render(request, "orgupdate.html", context)

    def post(self, request, org_id):
        if request.user.username != org_id:
            return redirect("/")

        context = {
            "org_id":org_id,
            "dashboard_url":"/clubs/" + org_id
        }

        try:
            org = Org.objects.filter(user=request.user)
            org = org[0] if org else org

            org.club_name = request.POST.get("org_name")
            org.club_address = request.POST.get("org_address")
            org.club_phone = request.POST.get("org_phone")
            org.club_contact_person = request.POST.get("org_contact_person")
            org.save()

            context["org_name"] = org.club_name
            context["org_address"] = org.club_address
            context["org_phone"] = org.club_phone
            context["org_contact_person"] = org.club_contact_person
            context["update_success"] = True
        except Exception as e:
            print e
            context["update_failure"] = True
        return render(request, "orgupdate.html", context)

""" User Views """
class UserView(View):
    def get(self, request, user_id):
        user = User.objects.get(username=user_id)
        events = Participation.objects.filter(user=user)

        context = {
            "full_name":user.first_name.title() + " " + user.last_name.title(),
            "user_name":user_id,
            "member_since":user.date_joined,
            "events":events
        }
        return render(request, "user.html", context)

""" Event Views """
class EventView(View):
    def get_context(self, request, org_id, event_id):
        event = Event.objects.filter(id=event_id)[0]

        context = {
            "event_id":event_id,
            "event_name":event.name,
            "event_desc":event.description,
            "event_date":event.date,
            "event_loc":event.location,
            "event_sched":event.schedule,
            "event_private":event.private,
            "org_status":request.user.username == org_id,
            "org_id":org_id,
            "org_volunteer":EventVolunteer.objects.filter(event=event),
            "org_request":EventPrivateInvitation.objects.filter(event=event, active=True),
            "unregister":False,
        }

        dashboard_url = "/clubs/" + org_id if context["org_status"] else "/users/" + request.user.username
        context["dashboard_url"] = dashboard_url

        if request.user.is_anonymous():
            return context
        elif Participation.objects.filter(event=event_id, user=request.user):
            context["unregister"] = True

        participants = Participation.objects.filter(event=event_id).order_by('order')
        registered_participants, players_record = [], []

        for p in participants:
            registered = User.objects.get(username=p.user.username)
            if registered:
                registered_participants.append(registered)
                try:
                    record = EventRecord.objects.filter(event=event_id, user=registered)[0]
                    players_record.append((record.tee, record.cart, record.flight, record.score))
                except Exception as e:
                    players_record.append(())
                    
        context["participants"] = zip(registered_participants, players_record)
        return context

    def process_event_requests(self, request, event, org_id, event_id, decision, get_list=True):
        if get_list:
            pending_requests = zip(request.POST.getlist("name"), request.POST.getlist("email"))
        else:
            pending_requests = zip([request.POST.get("name")], [request.POST.get("email")])

        util = Utility()
        for pr in pending_requests:
            try:
                request_name = pr[0]
                request_email = pr[1]

                event_request = EventPrivateInvitation.objects.filter(email=request_email, name=request_name, event=event)[0]
                event_request.invited = decision
                event_request.active = False
                event_request.save()

                if decision:
                    request_url = "http://looper-golf.herokuapp.com/clubs/%s/events/%s/%s/request" % (org_id, event_id, event_request.key)
                    subject = "Your request for " + event.name + " has been approved."
                    body = request_name + ", \nPlease click on this link to complete registration.<br>" + "<a href='" + request_url + "'>" + request_url + "</a>"
                    util.blast_emails(subject, body, [request_email], html=True)
            except Exception as e:
                print e

    def get(self, request, org_id, event_id):
        context = self.get_context(request, org_id, event_id)
        return render(request, "event.html", context)

    def post(self, request, org_id, event_id):
        context = self.get_context(request, org_id, event_id)
        event = Event.objects.get(id=event_id)
        if "blast_emails" in request.POST:
            util = Utility()
            try:
                emails = util.get_emails_from_events(Event.objects.filter(id=event_id))
                subject = request.POST.get("message_subject", "A Message from " + org_id)
                body = request.POST.get("message_body", "")
                html = True if request.POST.get("message_html") else False
                util.blast_emails(subject, body, emails, html=html)
                context["email_blast_success"] = True
            except Exception as e:
                print e
        elif "volunteer" in request.POST:
            email = request.POST.get("email")
            name = request.POST.get("fullname")
            role = request.POST.get("role")
            if not (email and name and role):
                context["volunteer_failure"] = True
            else:
                try:
                    if EventVolunteer.objects.filter(email=email):
                        context["volunteer_duplicate"] = True
                    else:
                        ev = EventVolunteer()
                        ev.event = event
                        ev.email = email
                        ev.name = name
                        ev.role = role
                        ev.save()
                        context["volunteer_success"] = True
                except Exception as e:
                    print e
        elif "volunteer_edit" in request.POST:
            try:
                EventVolunteer.objects.filter(event=event).delete()
                
                names = request.POST.getlist("name")
                emails = request.POST.getlist("email")
                roles = request.POST.getlist("role")

                for i in range(len(names)):
                    ev = EventVolunteer()
                    ev.event = event
                    ev.name = names[i]
                    ev.email = emails[i]
                    ev.role = roles[i]
                    ev.save()

                context["org_volunteer"] = EventVolunteer.objects.filter(event=event)
            except Exception as e:
                print e
        elif "private_request" in request.POST:
            try:
                email = request.POST.get("email")
                name = request.POST.get("name")

                if not (email and name):
                    context["private_request_failure"] = True
                elif EventPrivateInvitation.objects.filter(event=event, email=email):
                    context["private_request_duplicate"] = True
                else:
                    evi = EventPrivateInvitation()
                    evi.event = event
                    evi.name = name
                    evi.email = email
                    evi.key = str(int(time.time())) + os.urandom(16).encode('hex')
                    evi.save()
                    context["private_request_success"] = True
            except Exception as e:
                print e
        elif "request_approve_all" in request.POST:
            self.process_event_requests(request, event, org_id, event_id, True)
        elif "request_decline_all" in request.POST:
            self.process_event_requests(request, event, org_id, event_id, False)
        elif "request_approve" in request.POST:
            self.process_event_requests(request, event, org_id, event_id, True, get_list=False)
        elif "request_decline" in request.POST:
            self.process_event_requests(request, event, org_id, event_id, False, get_list=False)
        return render(request, "event.html", context)

class RearrangeView(View):
    def get(self, request, org_id, event_id):
        players = request.GET.get("p").split(",")
        tee = request.GET.get("tee").split(",")
        flight = request.GET.get("flight").split(",")
        cart = request.GET.get("cart").split(",")
        score = request.GET.get("score").split(",")

        Participation.objects.filter(event=event_id).delete()
        EventRecord.objects.filter(event=event_id).delete()

        event = Event.objects.get(id=event_id)
        for i, value in enumerate(players):
            p = Participation()
            p.event = event
            p.user = User.objects.get(username=value)
            p.order = i
            p.save()

            er = EventRecord()
            er.event = event
            er.user = User.objects.get(username=value)
            er.tee = tee[i]
            er.cart = cart[i]
            er.flight = flight[i]
            er.score = score[i]
            er.save()
        
        return redirect("/clubs/" + org_id + "/events/" + event_id)

class PrivateEventRequestView(View):
    def get(self, request, org_id, event_id, key):
        context = {
            "success":False,
            "dashboard_url": "/clubs/" + org_id
        }
        try:
            evi = EventPrivateInvitation.objects.filter(key=key, event=event_id)[0]
            if evi.invited:
                first_name, last_name = evi.name.split() if " " in evi.name else ("", "")
                p = Participation()
                p.event = evi.event
                p.user = User.objects.create_user(evi.key[:30], evi.email, first_name=first_name, last_name=last_name)
                p.order = 0
                p.save()
                evi.active = False
                evi.save()
                context["success"] = True
        except Exception as e:
            print e
        return render(request, "eventrequest.html", context)

class RegisterView(View):
    def get(self, request, org_id, event_id):
        try:
            if request.user.username == org_id:
                return redirect("/clubs/" + org_id)

            if Participation.objects.filter(event=event_id, user=request.user):
                return redirect("/clubs/" + org_id + "/events/" + event_id)

            event = Event.objects.get(id=event_id)
            par = Participation()
            par.event = event
            par.user = request.user
            par.order = 0
            par.save()

            subject = 'Registration for ' + event.name
            body = 'You have successfully registered for %s.\nLocation: %s\nDate: %s\n.' % (event.name, event.location, str(event.date))
            send_mail(subject, body, 'LooperGolf@example.com', ['v.long128@gmail.com'], fail_silently=False)
            
            return redirect("/clubs/" + org_id + "/events/" + event_id)
        except Exception as e:
            print e
            return redirect("/login")

class UnregisterView(View):
    def get(self, request, org_id, event_id):
        try:
            Participation.objects.filter(user=request.user, event=event_id).delete()
            send_mail('You have sucessfully unregistered for ' + event_id, 'Here is the message.', 'from@example.com', ['v.long128@gmail.com'], fail_silently=False)
        except Exception as e:
            print e
        return redirect("/clubs/" + org_id + "/events/" + event_id)

class OrgCreateView(View):
    def get(self, request, org_id):
        if request.user.is_anonymous() or request.user.username != org_id:
            return redirect("/")
        context = {
            "org_id": org_id,
            "dashboard_url": "/clubs/" + org_id
        }
        return render(request, "create.html", context)

    def post(self, request, org_id):
        context = {
            "org_id": org_id,
            "dashboard_url": "/clubs/" + org_id
        }
        if request.user.is_anonymous() or request.user.username != org_id:
            return redirect("/")
        try:
            event = Event()
            event.name = request.POST.get("event_name")
            event.description = request.POST.get("event_desc")
            event.location = request.POST.get("event_loc")
            event.date = request.POST.get("event_date")
            event.schedule = request.POST.get("event_sched")
            event.private = True if request.POST.get("event_private") == "Yes" else False
            event.organizer = request.user
            event.save()
            context["created"] = True
        except Exception as e:
            print e
            context["failed"] = True
        return render(request, "create.html", context)

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
        event_sched = request.POST.get("event_sched")
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
            if event_sched:
                event.schedule = event_sched
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