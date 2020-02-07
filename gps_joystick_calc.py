from inputs import get_gamepad
import time
import math
import subprocess
import re

sticks_codes = ['ABS_X', 'ABS_Y']

deadzone = 0.3

START_LOCATION_COMMAND = 'adb shell dumpsys location | grep "Location\[network"'
NEW_LOCATION_COMMAND = "adb shell am start-foreground-service -a theappninjas.gpsjoystick.TELEPORT --ef lng {0} --ef lat {1}"

dps = 2
kmh = 10

d = kmh/(3.6*dps)

def main():
    """Just print out some event infomation when the gamepad is used."""
    x,y = 0,0
    
    # Get current GPS coordinates from phone
    current_gps_raw = subprocess.check_output(START_LOCATION_COMMAND.split(" ")).decode('utf-8')
    best_gps_data = current_gps_raw.split('\n ')[-1]
    matches = re.search('([-]?\d+,\d+),([-]?\d+,\d+)', best_gps_data)

    lon, lat = float(matches.group(1).replace(',','.')),float(matches.group(2).replace(',','.'))

    t = time.time()
    while 1:
        events = get_gamepad()
        for event in events:
            if event.code == 'ABS_X':
                x = (event.state-128)/128
                if (x <= deadzone) and (x >= -1*deadzone):
                    x = 0
            if event.code == 'ABS_Y':
                y = (event.state-128)/128
                if (y < deadzone) and (y >= -1*deadzone):
                    y = 0
        elapsed = time.time() - t
        if elapsed >= (1/dps):
            nlon = lon + (180/math.pi)*(d*y/6378137)/math.cos(lat)
            nlat = lat +(180/math.pi)*(d*x/6378137)

            lon = nlon
            lat = nlat
            print('\r{0}, {1}'.format(d*y,d*x))
            print('\r{0}, {1}'.format(lon,lat))

            print(subprocess.check_output(NEW_LOCATION_COMMAND.format(lat,lon).split(" ")))

            t = time.time()

if __name__ == "__main__":
    main()
