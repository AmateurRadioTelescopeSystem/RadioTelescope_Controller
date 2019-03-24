#import astropy.coordinates as coord
from astropy.coordinates import SkyCoord, EarthLocation, FK5, ICRS

import astropy.units as units
from astropy.time import Time
import time
import ephem
from skyfield.api import load, Topos
import datetime

c = SkyCoord("5h40m45.54s", "+40d12m")
loc = EarthLocation(lat="40.6306", lon="22.9589", height="50")
print(loc)
print(float(loc.lon.to_string(decimal=True))/15)
print("   \n")

datetime.datetime(2019, 3, 23)
t = Time(datetime.datetime(2019, 3, 23), scale='utc', location=loc, format='datetime')
print("\n\n\n")
print(t)
print("\n\n\n")
FK5_Jnow = FK5(equinox=t)


print(t.format)
print(t.scale)
print(t)
start = time.time()
ha = -c.transform_to(FK5_Jnow).ra.to(units.hourangle) + t.sidereal_time('apparent')
end = time.time()
print(ha.to_string(decimal=True))
print(type(ha))
print(end - start)
print()
print(type(t.sidereal_time('apparent')))

ts = load.timescale()
tm = ts.utc(2019, 3, 23.916667)
print(tm.utc_datetime())
planets = load('de421.bsp')
earth = planets['earth']
thess = Topos('40.6306 N', '22.9589 E')
print(thess.longitude._hours)
# print(thess.at(tm).gast)
start = time.time()
lst = tm.gast + thess.longitude._hours
end = time.time()
print(end - start)
print("  \n")
print(int(lst))
print((lst - int(lst))*60)
print((((lst - int(lst))*60) - int((lst - int(lst))*60))*60)
print(tm.gast)


