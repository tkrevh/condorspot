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
import os.path
import StringIO

from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from ctypes import *
from condorspot.models import Competition, Event, Task, Turnpoint, SprintResult, fpl_to_cspot_compclass
from django.core.files import File
from PIL import Image
from mathutils import Point

###################################  TASK IMAGE GEN #################################


MAX_TASKIMG_WIDTH=640
MAX_TASKIMG_HEIGHT=480
CROP_MARGIN=50

class NaviConInitError(Exception):
    pass

def generate_task_img(flightplan, outputimg):
    image = get_task_img(flightplan)
    image.save(outputimg, 'JPEG');

def get_task_img(flightplan):

    # condor installation folder
    condorbase = "c:\\Program Files\\Condor"

    config = ConfigParser.ConfigParser()
    config.read(flightplan)
    landscape = config.get('Task', 'Landscape')
    trnfile = "c:\\Program Files\\Condor\\Landscapes\\" + landscape + "\\" + landscape + ".trn"

    windll.LoadLibrary(condorbase + '\\NaviCon.dll')
    windll.NaviCon.GetMaxY.restype = c_float
    windll.NaviCon.GetMaxX.restype = c_float
    windll.NaviCon.XYToLon.restype = c_float
    windll.NaviCon.XYToLat.restype = c_float
    if not windll.NaviCon.NaviConInit(c_char_p(trnfile)):
        raise NaviConInitError

    maxx = windll.NaviCon.GetMaxX()
    maxy = windll.NaviCon.GetMaxY()

    landscapefile = "c:\\Program Files\\Condor\\Landscapes\\" + landscape + "\\" + landscape + ".JPG"
    im = Image.open(landscapefile)
    im = im.copy()
    imagewidth = im.size[0]
    imageheight = im.size[1]
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    tasklayer = Image.new("RGBA", im.size, (0,0,0,0))
    taskdraw = ImageDraw.Draw(tasklayer)

    first = True
    lasttplat = 0
    lasttplon = 0
    lasttpx = 0
    lasttpy = 0
    bearing = 0
    cropx1 = imagewidth
    cropy1 = imageheight
    print "Scenery picture width="+str(imagewidth)+" height="+str(imageheight)
    cropx2 = 0
    cropy2 = 0
    for i in range(1, 100):
        istr = str(i)
        try:
            name = config.get('Task', 'TPName'+istr)
            posx = float(config.get('Task', 'TPPosX'+istr))
            posy = float(config.get('Task', 'TPPosY'+istr))
            posz = float(config.get('Task', 'TPPosZ'+istr))
            radius = float(config.get('Task', 'TPRadius'+istr))/150
            angle = int(config.get('Task', 'TPAngle'+istr))
        except ConfigParser.NoOptionError:
            break

        nextTPExists = True
        try:
            istr = str(i+1)
            nextname = config.get('Task', 'TPName'+istr)
            nextposx = float(config.get('Task', 'TPPosX'+istr))
            nextposy = float(config.get('Task', 'TPPosY'+istr))
            nextposz = float(config.get('Task', 'TPPosZ'+istr))
            nextradius = float(config.get('Task', 'TPRadius'+istr))/150
            nextangle = int(config.get('Task', 'TPAngle'+istr))
            nexttplat = windll.NaviCon.XYToLat(c_float(nextposx), c_float(nextposy))
            nexttplon = windll.NaviCon.XYToLon(c_float(nextposx), c_float(nextposy))
        except ConfigParser.NoOptionError:
            nextTPExists = False

        tplat = windll.NaviCon.XYToLat(c_float(posx), c_float(posy))
        tplon = windll.NaviCon.XYToLon(c_float(posx), c_float(posy))

        imgx = imagewidth-(posx/maxx)*imagewidth
        imgy = imageheight-(posy/maxy)*imageheight

        if imgx < cropx1:
            cropx1 = max(imgx - CROP_MARGIN, 0)
        if imgy < cropy1:
            cropy1 = max(imgy - CROP_MARGIN, 0)
        if imgx > cropx2:
            cropx2 = min(imgx + CROP_MARGIN, imagewidth)
        if imgy > cropy2:
            cropy2 = min(imgy + CROP_MARGIN, imageheight)

        textsize = taskdraw.textsize(name, font=None)
        if (i > 1) & (nextTPExists):
            tppt = Point(tplat, tplon)
            lastpt = Point(lasttplat, lasttplon)
            bearing = lastpt.bearing(tppt)
            if (i == 2):
                taskdraw.chord([lasttpx-15,lasttpy-15,lasttpx+15,lasttpy+15], bearing, bearing+180, outline="red")
            if (angle == 360):
                taskdraw.ellipse([imgx-radius, imgy-radius, imgx+radius, imgy+radius], outline=(255, 0, 0))
            else:
                nextpt = Point(nexttplat, nexttplon)
                nextbearing = tppt.bearing(nextpt)
                middlebearing = (bearing + nextbearing)/2
                taskdraw.pieslice([imgx-radius, imgy-radius, imgx+radius, imgy+radius], middlebearing-angle/2, middlebearing+angle/2, outline="red")
        if (i == 1):
            taskdraw.text([imgx, imgy+textsize[1]], "START: "+name, fill="blue")
        if (i > 1) & (nextTPExists):
            istr = str(i-1)
            taskdraw.text([imgx, imgy-textsize[1]], name+" ("+istr+")", fill="blue")
        if (i > 1) & (not nextTPExists):
            taskdraw.text([imgx, imgy-textsize[1]], "FINISH: "+name, fill="blue")
            tppt = Point(tplat, tplon)
            lastpt = Point(lasttplat, lasttplon)
            bearing = tppt.bearing(lastpt)
            taskdraw.chord([imgx-10,imgy-10,imgx+10,imgy+10], bearing, bearing+180, outline="red")

        if first:
            first = False
        else:
            taskdraw.line([(lasttpx,lasttpy),(imgx,imgy)], fill="#AA0000")
        lasttpx = imgx
        lasttpy = imgy
        lasttplat = tplat
        lasttplon = tplon
        lastbearing = bearing

    crop_width = max(cropx2 - cropx1, MAX_TASKIMG_WIDTH)
    crop_height = max(cropy2 - cropy1, MAX_TASKIMG_HEIGHT)

    crop_center_x = (cropx2 + cropx1)/2
    crop_center_y = (cropy2 + cropy1)/2

    width_oversize_factor = crop_width / MAX_TASKIMG_WIDTH
    height_oversize_factor = crop_height / MAX_TASKIMG_HEIGHT

    if (crop_center_x + crop_width/2) > imagewidth:
        crop_center_x = imagewidth - crop_width/2
    if (crop_center_x - crop_width/2) < 0:
        crop_center_x = crop_width/2
    if (crop_center_y + crop_height/2) > imageheight:
        crop_center_y = imageheight - crop_height/2
    if (crop_center_y - crop_height/2) < 0:
        crop_center_y = crop_height/2


    # draw task
    newImg = Image.composite(tasklayer, im, tasklayer)
    newImg = newImg.copy()
    print "cropping center_x="+str(crop_center_x)+" centery="+str(crop_center_y)+" width="+str(crop_width)+" height="+str(crop_height)
    newImg = newImg.crop([int(crop_center_x - crop_width/2), int(crop_center_y - crop_height/2), int(crop_center_x + crop_width/2), int(crop_center_y + crop_height/2)])

    if (width_oversize_factor > 1) & (width_oversize_factor > height_oversize_factor):
        aspect_ratio = width_oversize_factor
        newHeight = int(round(MAX_TASKIMG_HEIGHT/aspect_ratio))
        newImg = newImg.resize([MAX_TASKIMG_WIDTH, newHeight], Image.BICUBIC)
    if (height_oversize_factor > 1) & (width_oversize_factor < height_oversize_factor):
        aspect_ratio = height_oversize_factor
        newWidth = int(round(MAX_TASKIMG_WIDTH/height_oversize_factor))
        newImg = newImg.resize([newWidth, MAX_TASKIMG_HEIGHT], Image.BICUBIC)

    del taskdraw
    return newImg
