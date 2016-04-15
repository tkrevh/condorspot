import datetime
import sys
import os,fnmatch
import ConfigParser
import string
import csv, sys
import errno
import os
import shutil
import math
import StringIO
import os.path
import time
import decimal

from time import gmtime, strftime
from ctypes import *
from condorspot.models import Competition, Event, Task, Turnpoint, SprintResult, fpl_to_cspot_compclass
from imgutil import get_task_img, generate_task_img
from django.core.files import File


MAXTRIES = 5
STATUS_FINISHED = 'Finished'

def parse_task(fplfilename):
    fpl = ConfigParser.ConfigParser()
    fpl.read(fplfilename)

    taskdescr = fpl.get("Description", "Text")
    print "Task description = ",taskdescr
    tasktokens = taskdescr.split()
    competition_ref = tasktokens[0].strip()
    event_ref = tasktokens[1].strip()
    competition_class = fpl_to_cspot_compclass(fpl.get("Plane", "Class"))
    print "Competition = "+competition_ref
    print "Event = "+event_ref+", task is for class "+competition_class

    try:
        competition = Competition.objects.get(name=competition_ref)
    except Competition.DoesNotExist:
        print "ERROR: Competition "+competition_ref+" does not exist. Create it first. Exiting!"
        return

    try:
        event = Event.objects.get(name=event_ref, competition=competition)
    except Event.DoesNotExist:
        print "ERROR: event <"+event_ref+"> for competition "+competition.name+" does not exist, exiting!"
        return

    print "Loaded competition "+competition.name+" and event "+event.name

    print "Checking if task for competition class <"+competition_class+"> exists in Event "+event.name
    try:
        task = Task.objects.get(event=event, competition_class=competition_class)
        print "ERROR: task <"+task.name+"> for competition class "+competition_class+" alredy exists, exiting!"
        return
    except Task.DoesNotExist:
        # perfect, continue
        # task doesnt exist, go ahead an create one
        print "Task <"+event_ref+"> for "+competition_class+" class does not exists, creating new task..."
        task = Task()


    task.name = event_ref
    task.event = event
    task.landscape = fpl.get("Task", "Landscape")
    task.competition_class = fpl_to_cspot_compclass(fpl.get("Plane", "Class"))
    task.wind_direction = int(float(fpl.get("Weather", "WindDir")))
    task.wind_speed = int(float(fpl.get("Weather", "WindSpeed")))
    task.wind_dir_variation = fpl.get("Weather", "WindDirVariation")
    task.wind_speed_variation = fpl.get("Weather", "WindSpeedVariation")
    task.wind_turbulence = fpl.get("Weather", "WindTurbulence")
    task.thermals_temp = int(float(fpl.get("Weather", "ThermalsTemp")))
    task.thermals_temp_variation = fpl.get("Weather", "ThermalsTempVariation")
    task.thermals_dew = int(float(fpl.get("Weather", "ThermalsDew")))
    task.thermals_strength = fpl.get("Weather", "ThermalsStrength")
    task.thermals_strength_variation = fpl.get("Weather", "ThermalsStrengthVariation")
    task.thermals_inversion = int(float(fpl.get("Weather", "ThermalsInversionheight")))
    task.thermals_width = fpl.get("Weather", "ThermalsWidth")
    task.thermals_width_variation = fpl.get("Weather", "ThermalsWidthVariation")
    task.thermals_activity = fpl.get("Weather", "ThermalsActivity")
    task.thermals_turbulence = fpl.get("Weather", "ThermalsTurbulence")
    task.pressure = int(float(fpl.get("Weather", "Pressure")))
    task.start_time = fpl.get("GameOptions", "StartTime")
    task.start_window = fpl.get("GameOptions", "StartTimeWindow")
    task.start_delay = fpl.get("GameOptions", "RaceStartDelay")
    task.task_date = fpl.get("GameOptions", "TaskDate")
    task.allow_pda = fpl.get("GameOptions", "AllowPDA")
    task.start_type = fpl.get("GameOptions", "StartType")
    task.description = taskdescr
    srvrfplfilename = competition.name+"_"+event.name+"_"+task.competition_class+".fpl"
    f = open(fplfilename, 'r')
    myfile = File(f)
    task.fplfile.save(srvrfplfilename, myfile, save=True)
    myfile.close()

    taskpicfilename = competition.name+"_"+event.name+"_"+task.competition_class+".jpg"
    generate_task_img(fplfilename, taskpicfilename)
    f = open(taskpicfilename, 'rb')
    picfile = File(f)
    task.picture.save(taskpicfilename, picfile, save=True)
    picfile.close()

    task.save()

    tpidx = 0
    try:
        while (True):
            tpname = fpl.get("Task", "TPName"+`tpidx`)
            print "Found TP"+`tpidx`+" "+tpname
            tp = Turnpoint()
            tp.task = task
            tp.name = tpname
            tp.xpos = fpl.get("Task", "TPPosX"+`tpidx`)
            tp.ypos = fpl.get("Task", "TPPosY"+`tpidx`)
            tp.zpos = fpl.get("Task", "TPPosZ"+`tpidx`)
            tp.minheight = fpl.get("Task", "TPAltitude"+`tpidx`)
            tp.maxheight = fpl.get("Task", "TPHeight"+`tpidx`)
            tp.radius = fpl.get("Task", "TPRadius"+`tpidx`)
            tp.angle = fpl.get("Task", "TPAngle"+`tpidx`)
            tp.width = fpl.get("Task", "TPWidth"+`tpidx`)
            tp.azimuth = fpl.get("Task", "TPAzimuth"+`tpidx`)
            tpidx += 1
            tp.save()
    except ConfigParser.NoOptionError:
        # no more turnpoints
        return

def mark_processed(file):
    os.rename(file, get_processed_filename(file))

def mark_unprocessed(file):
    os.rename(file, get_processed_filename(file))

def get_processed_filename(file):
    return file+".done"


# convert *.done files back to original state for re-processing
def restore_done_files(folder):
    for donefileName in os.listdir (folder):
       if fnmatch.fnmatch ( donefileName, '*.done' ):
           print "Found file ",donefileName
           purefilename = os.path.splitext(donefileName)
           myfile_name_without_suffix = purefilename[0]
           os.rename(os.path.join(folder,donefileName), os.path.join(folder,myfile_name_without_suffix))
           print "Renamed <"+donefileName+"> to <"+myfile_name_without_suffix+">"


def parse_csv_results(folder):
    for csvfileName in os.listdir (folder):
       if fnmatch.fnmatch ( csvfileName, '*.csv' ):
           print "Found results file ",csvfileName
           purefilename = os.path.splitext(csvfileName)
           myfile_name_without_suffix = purefilename[0]
           for ftrfileName in os.listdir (folder):
              if fnmatch.fnmatch ( ftrfileName, myfile_name_without_suffix+'.fpl' ):
                 print "Also found "+ftrfileName
                 fpl = ConfigParser.ConfigParser()
                 fpl.read(folder+ftrfileName)
                 taskdescr = fpl.get("Description", "Text")
                 competition_class = fpl_to_cspot_compclass(fpl.get("Plane", "Class"))
                 print "Task description = "+taskdescr
                 tasktokens = taskdescr.split()
                 competition_ref = tasktokens[0].strip()
                 event_ref = tasktokens[1].strip()

                 try:
                     competition = Competition.objects.get(name=competition_ref)
                 except Competition.DoesNotExist:
                     print "ERROR: Competition "+competition_ref+" does not exist. Exiting!"
                     return

                 try:
                     event = Event.objects.get(name=event_ref, competition=competition)
                 except Event.DoesNotExist:
                     print "ERROR: event <"+event_ref+"> for competition "+competition.name+" does not exist, exiting!"
                     return

                 print "Checking if task <"+event_ref+"> for "+competition_class+" class alredy exists"
                 try:
                     task = Task.objects.get(event=event, competition_class=competition_class)
                 except Task.DoesNotExist:
                     print "ERROR: Task in Event <"+event.name+"> for "+competition_class+" class does not exist, exiting!"
                     return
                 break
           try:
              stat = os.stat(folder+csvfileName)
              file_time = stat.st_mtime
              mark_processed(folder+csvfileName)
              mark_processed(folder+ftrfileName)
              print "Successfully renamed "+folder+csvfileName+" and "+folder+ftrfileName+" for processing !"
              source = csv.reader(open(get_processed_filename(folder+csvfileName), "rb"))
              line = 0
              for Rank,Status,Player,CN,RN,Plane,Dist,Time,Speed,Penalty,Score,TeamScore,Team in source:
                 print Rank,Status,Player,CN,RN,Plane,Dist,Time,Speed,Penalty,Score,TeamScore,Team
                 if (line > 0):
                     playertok = Player.split('.')
                     fname = playertok[0]
                     lname = playertok[1]
                     speed = decimal.Decimal(Speed.split()[0])
                     distance = decimal.Decimal(Dist.split()[0])
                     penalties = decimal.Decimal(Penalty.split()[0])
                     isbetterspeed = True
                     isbetterdistance = True
                     try:
                         result = SprintResult.objects.get(task=task.id, callsign=CN, firstname=fname, lastname=lname)
                         print "Found result for this player, checking it is better"
                         if (speed < result.speed):
                            isbetterspeed = False
                         if (distance < result.distance):
                            isbetterdistance = False
                         print "Better speed="+str(isbetterspeed)
                         print "Better distance="+str(isbetterdistance)
                     except SprintResult.DoesNotExist:
                         print "No result found yet for this player"
                         result = SprintResult()
                         result.tries = 0

                     if (result.tries < MAXTRIES):
                         result.task = task
                         result.callsign = CN
                         result.firstname = fname
                         result.lastname = lname
                         result.glider = Plane
                         result.registration_number = RN
                         if (Status == STATUS_FINISHED):
                            if (isbetterspeed):
                                result.time = Time
                                result.speed = speed
                                result.distance = distance
                                result.penalty = int(penalties)
                                time1 = gmtime(file_time)
                                result.date = datetime.datetime(year=time1.tm_year, month=time1.tm_mon, day=time1.tm_mday, hour=time1.tm_hour, minute=time1.tm_min, second=time1.tm_sec)
                                result.status = Status
                         else:
                            if (isbetterdistance):
                                result.time = Time
                                result.speed = 0
                                result.distance = distance
                                result.penalty = int(penalties)
                                time1 = gmtime(file_time)
                                result.date = datetime.datetime(year=time1.tm_year, month=time1.tm_mon, day=time1.tm_mday, hour=time1.tm_hour, minute=time1.tm_min, second=time1.tm_sec)
                                result.status = Status
                     result.tries = result.tries + 1
                     result.save()
                     print "Saved result for "+Player
                 line += 1
              print "-- END of ",csvfileName," -- "
           except IOError:
              print "File "+folder+csvfileName+" is still locked, will process it later !"
           #except:
           #    print "Unexpected error:", sys.exc_info()[0]




