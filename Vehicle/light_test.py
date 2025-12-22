import board #type:ignore
import neopixel #type:ignore
pixels = neopixel.NeoPixel(board.D18, 30)

pixels.fill((0, 255, 0))