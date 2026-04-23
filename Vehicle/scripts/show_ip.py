from rpi_lcd import LCD # type: ignore
import subprocess
from time import sleep
sleep(10)  # wait for WIFI to initialize

# Right now this runs on boot, once I get the other code good enough so that it can start on boot,
# We'll just call this from there.

# detect Pi's IP
def get_ip():
    try:
        result = subprocess.check_output("hostname -I", shell=True).decode().split()
        return result[0] if result else "No IP"
    except:
        return "Error"

lcd = LCD(address=0x27)

ip = get_ip()
lcd.text("Tank Online", 1)
lcd.text(ip, 2)

# keep displayed
try:
    while True:
        sleep(10)
        ip = get_ip()
        lcd.text(ip, 2)
except KeyboardInterrupt:
    lcd.clear()
