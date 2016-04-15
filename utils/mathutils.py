import math

def to_dms(angle):
    """
    Convert decimal angle to degrees, minutes and seconds notation

    >>> to_dms(52.015)
    (True, 52, 0, 54)
    >>> to_dms(-0.221)
    (False, 0, 13, 15)

    @type angle: C{float} or coercible to C{float}
    @param angle: Angle to convert
    @rtype: C{tuple} of C{bool} for sign and C{int}s for values
    @return: Angle converted to degrees, minutes and seconds
    """
    if angle < 0:
        sign = False
        angle = abs(angle)
    else:
        sign = True
    degrees = math.floor(angle)
    minutes = math.floor((angle - degrees) * 60)
    seconds = math.floor((angle - degrees - minutes / 60) * 3600)
    return sign, int(degrees), int(minutes), int(seconds)

class Point:
    """
    Simple class for representing a location on a sphere

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    """

    def __init__(self, latitude=0, longitude=0):
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __repr__(self):
        return "Point(%f, %f)" % (self.latitude, self.longitude)

    def as_rad(self):
        return math.radians(self.latitude), math.radians(self.longitude)

    def distance(self, other, method="haversine"):
        self_latitude, self_longitude = self.as_rad()
        other_latitude, other_longitude = other.as_rad()
        longitude_difference = other_longitude - self_longitude
        latitude_difference = other_latitude - self_latitude

        earth_radius = 6370 #kM

        if method == "haversine":
            temp = math.sin(latitude_difference / 2) ** 2 + \
                   math.cos(self_latitude) * \
                   math.cos(other_latitude) * \
                   math.sin(longitude_difference / 2) ** 2
            return 2 * earth_radius * math.atan2(math.sqrt(temp),
                                                 math.sqrt(1-temp))
        elif method == "sloc":
            return math.acos(math.sin(self_latitude) * \
                             math.sin(other_latitude) + \
                             math.cos(self_latitude) * \
                             math.cos(other_latitude) * \
                             math.cos(longitude_difference)) * earth_radius
        else:
            raise ValueError("Unknown method type `%s'" % method)

    def bearing(self, other):
        self_latitude, self_longitude = self.as_rad()
        other_latitude, other_longitude = other.as_rad()
        longitude_difference = other_longitude - self_longitude

        y = math.sin(longitude_difference) * math.cos(other_latitude)
        x = math.cos(self_latitude) * math.sin(other_latitude) - \
            math.sin(self_latitude) * math.cos(other_latitude) * \
            math.cos(longitude_difference)
        bearing = math.degrees(math.atan2(y,x))
        # Always return positive North-aligned bearing
        return (bearing + 360) % 360
