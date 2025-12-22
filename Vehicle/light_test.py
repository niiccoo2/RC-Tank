import board #type:ignore
import neopixel #type:ignore
import time
pixels = neopixel.NeoPixel(board.D18, 30)

for i in range(30):
    if i < 6:
        pixels[i] = (0, 255, 0)
    elif i > 26:
        pixels[i] = (255, 0, 0)
    else:
        pixels[i] = (255, 255, 255)

time.sleep(10)
pixels.fill((0, 0, 0))