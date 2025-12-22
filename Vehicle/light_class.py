import board #type:ignore
import neopixel #type:ignore

class Lights:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, 30)
        self.pixels.fill((0, 0, 0))

    def run_lights(self):
        for i in range(30):
            if i < 6:
                self.pixels[i] = (0, 255, 0)
            elif i > 23:
                self.pixels[i] = (255, 0, 0)
            else:
                self.pixels[i] = (255, 255, 255)
    
    def headlights_off(self):
        for i in range(30):
            if i > 6 and i < 24:
                self.pixels[i] = (0, 0, 0)
    
    def off(self):
        self.pixels.fill((0, 0, 0))