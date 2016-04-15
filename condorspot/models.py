import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

COMPETITION_TYPES = (
('1', 'SPRINT'),
('2', 'CUP'),
)

COMPETITION_CLASSES = (
('std', _('std')),
('15m', _('15m')),
('18m', _('18m')),
('open', _('open')),
('mixed', _('mixed')),
)

COMPETITION_CLASSES_DICT = {
'Standard': 'std',
'15-meter': '15m',
'18-meter': '18m',
'Open': 'open',
'All': 'mixed'
}

GENDER =(
('m', _('Male')),
('f', _('Female')),
)

IMAGE_SIZES = {'thumbnail' : (150, 150)}

def fpl_to_cspot_compclass(fplcompclass):
    return COMPETITION_CLASSES_DICT[fplcompclass]

# CondorSpot model

class Competition(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    description = models.CharField(_("Description"), max_length=2048)
    from_date = models.DateField(_("From date"), blank=True, null=True)
    to_date = models.DateField(_("To date"), blank=True, null=True)
    picture = models.ImageField(_("Picture"), upload_to="img/", blank=True, null=True)
    type = models.CharField(_("Competition type"), max_length=1, choices = COMPETITION_TYPES)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _("Competition")
        verbose_name_plural = _("Competitions")

class Event(models.Model):
    competition = models.ForeignKey(Competition)
    name = models.CharField(_("Name"), max_length=100)
    from_date = models.DateField(_("From date"), blank=True, null=True)
    to_date = models.DateField(_("To date"), blank=True, null=True)

    def __unicode__(self):
        return u'%s from %s to %s' % (self.name, self.from_date, self.to_date)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

class Task(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(_("Name"), max_length=100)
    landscape = models.CharField(_("Landscape"), max_length=100)
    competition_class = models.CharField(_("Competition class"), max_length=8, choices = COMPETITION_CLASSES)
    wind_direction = models.IntegerField(_("Wind direction"))
    wind_speed = models.IntegerField(_("Wind speed"))
    wind_dir_variation = models.IntegerField(_("Wind direction variation"))
    wind_speed_variation = models.IntegerField(_("Wind speed variation"))
    wind_turbulence = models.IntegerField(_("Wind turbulence"))
    thermals_temp = models.IntegerField(_("Thermal start temperature"))
    thermals_temp_variation = models.IntegerField(_("Thermal temperature variation"))
    thermals_dew = models.IntegerField(_("Dew point"))
    thermals_strength = models.IntegerField(_("Thermal strength"))
    thermals_strength_variation = models.IntegerField(_("Thermal strength variation"))
    thermals_inversion = models.IntegerField(_("Inversion height"))
    thermals_width = models.IntegerField(_("Thermals width"))
    thermals_width_variation = models.IntegerField(_("Thermals width variation"))
    thermals_activity = models.IntegerField(_("Thermals activity"))
    thermals_turbulence = models.IntegerField(_("Thermals turbulence"))
    pressure = models.DecimalField(_("Pressure"), max_digits=8, decimal_places=2)
    start_time = models.CharField(_("Name"), max_length=10)
    start_window = models.DecimalField(_("Start window"), max_digits=20, decimal_places=10)
    start_delay = models.DecimalField(_("Start delay"), max_digits=20, decimal_places=10)
    task_date = models.CharField(_("Task date"), max_length=10)
    allow_pda = models.IntegerField(_("Allow PDA"))
    start_type = models.IntegerField(_("Start type"))
    description = models.CharField(_("Task description"), max_length=1024)
    picture = models.ImageField(_("Picture"), upload_to="taskimg/", blank=True, null=True)
    thumbnail = models.ImageField(_("Thumbnail"), upload_to="taskthumbs/", blank=True, null=True)
    fplfile = models.FileField(_("Flightplan file"), upload_to="fpl/", blank=False, null=False)

    def save(self):
        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.base import ContentFile

        super(Task, self).save()

        if not self.picture:
            return

        #Original photo
        imgFile = Image.open(self.picture.path)

        #Convert to RGB
        if imgFile.mode not in ('L', 'RGB'):
            imgFile = imgFile.convert('RGB')

        #Save a thumbnail for each of the given dimensions
        for field_name, size in IMAGE_SIZES.iteritems():
            field = getattr(self, field_name)
            working = imgFile.copy()
            working.thumbnail(size, Image.ANTIALIAS)
            fp = StringIO()
            working.save(fp, "JPEG", quality=95)
            cf = ContentFile(fp.getvalue())
            field.save(name=self.picture.name, content=cf, save=False);

        #Save instance of Photo
        super(Task, self).save()

    def __unicode__(self):
        return u'%s %s' % (self.name, self.competition_class)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

class Turnpoint(models.Model):
    task = models.ForeignKey(Task)
    name = models.CharField(_("Name"), max_length=100)
    xpos = models.DecimalField(_("X"), max_digits=20, decimal_places=10)
    ypos = models.DecimalField(_("Y"), max_digits=20, decimal_places=10)
    zpos = models.DecimalField(_("Z"), max_digits=20, decimal_places=10)
    minheight = models.IntegerField(_("Minimum Height"))
    maxheight = models.IntegerField(_("Maximum Height"))
    radius = models.IntegerField(_("Radius"))
    angle = models.IntegerField(_("Angle"))
    width = models.IntegerField(_("Width"))
    azimuth = models.IntegerField(_("Azimuth"))

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _("Turnpoint")
        verbose_name_plural = _("Turnpoints")

class SprintResult(models.Model):
    task = models.ForeignKey(Task)
    callsign = models.CharField(_("Callsign"), max_length=3)
    firstname = models.CharField(_("First Name"), max_length=50)
    lastname = models.CharField(_("Last Name"), max_length=50)
    glider = models.CharField(_("Glider"), max_length=50)
    registration_number = models.CharField(_("Registration Number"), max_length=10)
    speed = models.DecimalField(_("Speed"), max_digits=20, decimal_places=2)
    time = models.CharField(_("Task time"), max_length=50)
    tries = models.IntegerField(_("Number of tries"))
    date = models.DateTimeField(_("Date of flight"), null=True, blank=True)
    penalty = models.IntegerField(_("Penalty"))
    distance = models.DecimalField(_("Distance"), max_digits=20, decimal_places=2)
    status = models.CharField(_("Status"), max_length=50)

    def __unicode__(self):
        return u'Task %s %s %s' % (self.task.name, self.callsign, self.speed)

    def taskname(self):
        return self.task.name

    class Meta:
        verbose_name = _("Sprint Result")
        verbose_name_plural = _("Sprint Results")

class Competitor(models.Model):
    firstname = models.CharField(_("First Name"), max_length=50)
    lastname = models.CharField(_("Last Name"), max_length=50)
    gender = models.CharField(_("Gender"), max_length=1, choices = COMPETITION_CLASSES)
    email = models.EmailField(_("Email"), max_length=50)
    password = models.CharField(_("Password"), max_length=50)
    country = models.CharField(_("Country"), max_length=2)
    rlh = models.IntegerField(_("RL hours"))
    rlk = models.IntegerField(_("RL kilometers"))
    cn = models.CharField(_("Last Name"), max_length=3)
    rn = models.CharField(_("Last Name"), max_length=10)

    lastlogin = models.DateTimeField(_("Last login"), default=datetime.datetime.now)
    lastpasswordcheck = models.DateTimeField(_("Last password check"), default=datetime.datetime.now)
    datejoined = models.DateTimeField(_("Date joined"), default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % self.email

    class Meta:
        verbose_name = _("Competitor")
        verbose_name_plural = _("Competitors")