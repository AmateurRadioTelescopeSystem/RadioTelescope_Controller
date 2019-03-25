# import astropy.coordinates as coord
from astropy.coordinates import SkyCoord, EarthLocation, FK5, ICRS
from astropy import coordinates as coord

import astropy.units as units
from astropy.time import Time
import time
import ephem
from skyfield.api import load, Topos
import datetime
import numpy as np

c = SkyCoord(ra="5h40m45.54s", dec="-1d56m33.2s", unit='deg', frame=FK5, equinox='J2000')
# c.transform_to(frame='what')
loc = EarthLocation.from_geodetic(lat="40.6436", lon="22.9308")

print(loc)
print(float(loc.lon.to_string(decimal=True))/15)
print("   \n")

datetime.datetime(2019, 3, 23, 22)
t = Time(datetime.datetime(2019, 3, 23, 22), scale='utc', location=loc, format='datetime')
aa_frame = coord.AltAz(obstime=t, location=loc)
print(c.ra.hms)
print(c.dec.dms)
co = c.transform_to(FK5(equinox=t))
print(co.ra.hms)
print(co.dec.dms)
aa_coos = co.transform_to(aa_frame)

print("AltAz")
print(aa_coos.az, aa_coos.alt)
'''
print("\n\n\n")
print(t)
print("\n\n\n")
FK5_Jnow = FK5(equinox=t)
'''
'''
print(t.format)
print(t.scale)
print(t)
start = time.time()
ha = -c.transform_to(FK5_Jnow).ra.to(units.hourangle) + t.sidereal_time('apparent')
end = time.time()
print("Degs")
print(ha.degree)
print(type(ha.degree))
print(end - start)
print()
print(type(t.sidereal_time('apparent')))

ts = load.timescale()
tm = ts.utc(2019, 3, 23, 22, 0, 0)
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
'''
print("Planet section")
ts = load.timescale()
t = ts.now()
planets = load('de421.bsp')
mars = planets['Moon']
print(ts.now().tt + 20)
tup = (2019, 3, 23, 22, 0, 0)
print((*tup[:5], 8))
print(ts.utc(*tup[:5], tup[5] + 20).utc_datetime())


