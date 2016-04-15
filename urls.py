from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    url(r"^admin/(.*)", admin.site.root),

    url(r"^$", "condor.condorspot.views.front"),
    url(r"^register/$", "condor.condorspot.views.register"),
    url(r"^login/$", "condor.condorspot.views.login"),
    url(r"^profile/$", "condor.condorspot.views.profile"),
    url(r"^competitors/$", "condor.condorspot.views.competitors"),

    url(r"^sprint/$", "condor.condorspot.views.sprint_front"),
    url(r"^sprint/(?P<en>\d+)/(?P<cid>[0-9,a-z]{3,5})/$", "condor.condorspot.views.sprint_detail"),
    url(r"^sprint/info", "condor.condorspot.views.sprint_info"),
    url(r"^sprint/rules", "condor.condorspot.views.rules"),

    url(r"^x/servers/$", "condor.condorspot.views.servers"),
    url(r"^x/servers/(?P<cid>[0-9,a-z]{3,5})/$", "condor.condorspot.views.servers"),
)