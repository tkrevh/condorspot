from django import template
from django.template import RequestContext
from django.conf import settings
from condor.condorspot import models as models

register = template.Library()

### SIMPLE TAGS
@register.simple_tag
def css(request):
    compid = request.path.split("/")[1]
    if(compid==str(models.COMPETITION_TYPES[0][1]).lower()
    or compid=="register"
    or compid=="profile"
    or compid=="login"
    or compid=="competitors"
    ):
        return "styles_sprint.css"
    elif (compid==str(models.COMPETITION_TYPES[1][1]).lower()):
        return "styles_cup.css"
    else:
        return "styles_front.css"

@register.simple_tag
def title(request):
    title=""
    if(len(request.path.split("/"))>2):
        title += " - "+str(request.path.split("/")[1]).capitalize()
    if(len(request.path.split("/"))>3):
        title+= " - "+str(request.path.split("/")[3]).capitalize()
    return title

@register.simple_tag
def media_root(request=None):
    return str(settings.MEDIA_ROOT)