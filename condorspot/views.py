import datetime
import urllib2
import socket

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.sessions.models import Session
from django.views.generic import simple, list_detail
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from condor.condorspot.models import Event, SprintResult, Competitor, Task, Turnpoint

COMPETITION_CLASSES_DICT = {"mixed": "Mixed","std": "Standard","open": "Open","15m": "15-meter","18m": "18-meter",}
COMPETITION_CLASSES = ["std","15m","18m","open","mixed"]
SERVERS_LIST_URL = "http://condorsoaring.com/serverlist.php?output=raw"
#SERVERS_LIST_URL = "http://soaringsim.com/serverlist.php?output=raw"
TIMEOUT = 10 #seconds

def front(request):
    event = list(Event.objects.all().filter(competition=1, from_date__lte=datetime.datetime.now()).order_by("-from_date"))[0]
    return render_to_response("index_front.html", {"navigation_list":get_navigation("sprint", event.name)}, context_instance = RequestContext(request))

def sprint_front(request):
    events = list(Event.objects.all().filter(competition=1, from_date__lte=datetime.datetime.now()).order_by("-from_date")[:4])

    current_leaders =  list()
    for event in events[:1]:
        for key in COMPETITION_CLASSES:
            task = Task.objects.get(event=event.id, competition_class=key)
            results = list(SprintResult.objects.all().filter(task = task.id).order_by("-speed", "-distance")[:10])
            while(len(results) < 10): results.append(SprintResult.objects.none())
            current_leaders.append((event.name, key, {COMPETITION_CLASSES_DICT[key]:results}))

    previous_winners =  list()
    for event in events[1:]:#TODO SET BACK TO [1:]
        sprints =  list()
        for key in COMPETITION_CLASSES:
            task = Task.objects.get(event=event.id, competition_class=key)
            results = list(SprintResult.objects.all().filter(task = task.id).order_by("-speed", "-distance")[:3])
            sprints.append({key: {COMPETITION_CLASSES_DICT[key]:results}})
        previous_winners.append({event:sprints})

    return render_to_response("index_sprint_content_front.html", {"event":events[0], "navigation_list":get_navigation("sprint",events[0].name),"current_leaders_list":current_leaders, "previous_winners_list":previous_winners}, context_instance = RequestContext(request))

def sprint_detail(request, en = 0, cid = 0):
    results = None
    task = None
    turnpoints = None
    events = list(Event.objects.all().filter(competition=1, from_date__lte=datetime.datetime.now()).order_by("-from_date"));
    if(en==0 or cid==0):
        task = Task.objects.none()
        turnpoints = Turnpoint.objects.none()
        results = SprintResult.objects.none()
    else:
        event = Event.objects.get(competition=1, name = en, from_date__lte=datetime.datetime.now())
        task = Task.objects.get(event=event.id, competition_class=cid)
        turnpoints = list(Turnpoint.objects.all().filter(task=task.id).order_by("-id"))[:-1]
        results = SprintResult.objects.all().filter(task = task.id).order_by("-speed", "-distance")
    return render_to_response("index_sprint_content_detail.html", {"event" : str(en), "class" : str(cid), "task":task, "turnpoints_list":turnpoints, "navigation_list":get_navigation("sprint", en, cid),"results_list":results, "history_list":events[1:]}, context_instance = RequestContext(request))

def sprint_info(request):
    event = list(Event.objects.all().filter(competition=1, from_date__lte=datetime.datetime.now()).order_by("-from_date"))[0]
    return render_to_response("index_sprint_content_info.html", {"navigation_list":get_navigation("sprint",event.name)}, context_instance = RequestContext(request))

def cup(request, pid):
    return HttpResponse(request.path)

def competitors(request):
    return simple.direct_to_template(
            request,
            template="index_competitors.html",
            )
competitors.__doc__ = simple.direct_to_template.__doc__

def upload(request, pid):
    return HttpResponse(request.path)

def register(request):
    competitor = Competitor()
    competitor.firstname = "Janez"
    competitor.lastname = "Kranjski"
    competitor.gender = "m"
    competitor.email = "janez.kranjski@email.com"
    competitor.password = "password"
    competitor.country = "si"
    competitor.rlh = "500"
    competitor.rlk = "20000"
    competitor.cn = "6"
    competitor.rn = "S5-LEET"
    #competitor.save()

    return simple.direct_to_template(
            request,
            template="index_register.html",
            )
register.__doc__ = simple.direct_to_template.__doc__

def login(request):
    return simple.direct_to_template(
            request,
            template="index_login.html",
            )
login.__doc__ = simple.direct_to_template.__doc__

def profile(request):
    return simple.direct_to_template(
            request,
            template="index_profile.html",
            )
profile.__doc__ = simple.direct_to_template.__doc__

def rules(request, pid):
    return HttpResponse(request.path)

def servers(request, cid=0):
    return render_to_response("x_servers.html", {"servers":get_servers(cid)}, context_instance = RequestContext(request))

#METHODS
def get_navigation(competition, eventid, selected=""):
    navigation =  list()
    for key in COMPETITION_CLASSES: #url, class, style
        style=""
        if(key==selected): style=" class=\"sc\""
        navigation.append(("/"+str(competition)+"/"+str(eventid)+"/"+str(key), key, style))
    return navigation

def get_servers(cid=0):
    socket.setdefaulttimeout(TIMEOUT)
    servers=list()
    try:
        stream = urllib2.urlopen(SERVERS_LIST_URL)
        data = stream.read()
        stream.close()
        data = data.split("\n")
        for line in data:
            server = line.split("||")
            if len(server) > 3:
                if(server[3].lower().startswith("condorspot")):
                    if(cid != 0):
                        if(not server[3].lower().endswith(cid)):
                            continue
                    classname=""
                    for cc in COMPETITION_CLASSES:
                        if(server[3].lower().endswith(cc)): classname=cc
                    servers.append({
                    "cid":str(cid),
                    "competition":server[1],
                    "class":classname,
                    "url":server[2],
                    "name":server[3],
                    "scenery":server[4],
                    "status":server[5],
                    "players":server[6],
                    "private":server[7],
                    "uptime":server[8],
                    "distance":server[9],
                    "flown":server[10],
                    "leader":server[11],
                    })
    except IOError, e:
        servers.append("Could not fetch servers info from master server. ("+str(e.reason)+")")
    return servers