#!/usr/bin/env python

import os
import sys

from ctypes import *

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from condorspot.models import Task, Turnpoint

def convert():
    # condor installation folder
    condorbase = "c:\\Program Files\\Condor"
    windll.LoadLibrary(condorbase + '\\NaviCon.dll')
    windll.NaviCon.GetMaxY.restype = c_float
    windll.NaviCon.GetMaxX.restype = c_float
    windll.NaviCon.XYToLon.restype = c_float
    windll.NaviCon.XYToLat.restype = c_float

    tasks = list(Task.objects.all())
    for task in tasks:
        trnfile = "c:\\Program Files\\Condor\\Landscapes\\" + task.landscape + "\\" + task.landscape + ".trn"
        if not windll.NaviCon.NaviConInit(c_char_p(trnfile)):
            raise NaviConInitError

        turnpoints = list(Turnpoint.objects.all().filter(task=task.id))
        for turnpoint in turnpoints:

            if(turnpoint.xpos > 100 and turnpoint.ypos > 100): # A BIT LAME CHECK TO GET UNCONVERTED TURNPOINTS COORDS BUT IT WILL DO THE TRICK

                #Condor -> Deg
                lat = windll.NaviCon.XYToLat(c_float(turnpoint.xpos), c_float(turnpoint.ypos))
                lon = windll.NaviCon.XYToLon(c_float(turnpoint.xpos), c_float(turnpoint.ypos))
                turnpoint.xpos = str(lat)[:13]
                turnpoint.ypos = str(lon)[:13]
                turnpoint.save()

                #print "new GLatLng(" + str(lat)+","+str(lon)+"),"
                print "Turnpoint "+str(turnpoint.name)+" ("+str(lat)+","+str(lon)+") saved."

    return

if __name__=="__main__":
    print ""
    print "Script will loop throu all turnpoints in database, check each if its still unconverted, convert and save changes to database."
    print ""
    print "Just uncomment last line in script, wich is a call to convert() method and the script will run. Security reason :)."
    convert()