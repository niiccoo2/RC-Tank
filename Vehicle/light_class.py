import board #type:ignore
import neopixel #type:ignore

class Lights:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.GPIO_P18, 30)
        self.pixels.fill((0, 0, 0))

        self.side_value = 100

    def all_on(self):
        for i in range(30):
            if i < 6:
                self.pixels[i] = (0, self.side_value, 0)
            elif i > 23:
                self.pixels[i] = (self.side_value, 0, 0)
            else:
                self.pixels[i] = (255, 255, 255)
    
    def side_on(self):
        for i in range(30):
            if i < 6:
                self.pixels[i] = (0, self.side_value, 0)
            elif i > 23:
                self.pixels[i] = (self.side_value, 0, 0)
    
    def headlights_off(self):
        for i in range(30):
            if i > 5 and i < 24:
                self.pixels[i] = (0, 0, 0)

    def headlights_on(self):
        for i in range(30):
            if i > 5 and i < 24:
                self.pixels[i] = (255, 255, 255)
    
    def off(self):
        self.pixels.fill((0, 0, 0))