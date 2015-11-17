from django.conf.urls import patterns, include, url
from django.contrib import admin
from root.views import IndexView, LoginView, SignUpView, EventView, RegisterView, CreateView, LogoutView, OrgSignUpView, OrgView, OrgEditView, OrgDeleteView, UnregisterView, RearrangeView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view()),
    url(r'^login/', LoginView.as_view()),
    url(r'^logout/', LogoutView.as_view()),
    url(r'^signup/', SignUpView.as_view()),
    url(r'^orgsignup/', OrgSignUpView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/edit/$', OrgEditView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/delete/$', OrgDeleteView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/register$', RegisterView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/unregister$', UnregisterView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/rearrange$', RearrangeView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/create/$', CreateView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/$', OrgView.as_view()),
    url(r'^clubs/(?P<org_id>[\w]+)/events/(?P<event_id>[0-9]+)/$', EventView.as_view()),
]