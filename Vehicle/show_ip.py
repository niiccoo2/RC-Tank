from rpi_lcd import LCD # type: ignore
import subprocess
from time import sleep

# detect Pi's IP
def get_ip():
    try:
        result = subprocess.check_output("hostname -I", shell=True).decode().split()
        return result[0] if result else "No IP"
    except:
        return "Error"

lcd = LCD(address=0x27)
lcd.backlight_on()

ip = get_ip()
lcd.text("Tank Online", 1)
lcd.text(f"IP: {ip}", 2)

# keep displayed
try:
    while True:
        sleep(60)
        ip = get_ip()
        lcd.text(f"IP: {ip}", 2)
except KeyboardInterrupt:
    lcd.clear()
