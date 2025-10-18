from rpi_lcd import LCD # type: ignore
from time import sleep

lcd = LCD()

lcd.text('Hello World!', 1)
lcd.text('Raspberry Pi', 2)

sleep(5)
lcd.clear()