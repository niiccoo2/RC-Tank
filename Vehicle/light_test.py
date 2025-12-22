import board #type:ignore
import neopixel #type:ignore
import time
pixels = neopixel.NeoPixel(board.D18, 30)

pixels.fill((0, 255, 0))
time.sleep(10)
pixels.fill((0, 0, 0))