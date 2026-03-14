from periphery import SPI #type:ignore
import time

class Lights:
    def __init__(self, num_pixels=30):
        # Jetson Orin Nano SPI defaults (spidev0.0 @ 6.4 MHz)
        self.spi = SPI("/dev/spidev0.0", 0, 6400000)
        self.num_pixels = num_pixels
        self.pixels = [(0, 0, 0)] * num_pixels  # RGB tuples
        self.side_value = 100
        self._update_strip()
    
    def _rgb_to_spi(self, r, g, b):
        """Convert RGB values to SPI bit pattern for NeoPixels"""
        # NeoPixels expect GRB format
        grb = (g << 16) | (r << 8) | b
        spi_data = []
        
        # One LED bit per SPI byte at 6.4MHz gives 1.25us/bit.
        # 0-bit: ~0.31us high + 0.94us low; 1-bit: ~0.62us high + 0.62us low.
        for i in range(23, -1, -1):  # 24 bits, MSB first
            if (grb >> i) & 1:
                spi_data.extend([0b11110000])  # Logic 1 pulse
            else:
                spi_data.extend([0b11000000])  # Logic 0 pulse
        
        return spi_data
    
    def _update_strip(self):
        """Send current pixel data to the strip"""
        spi_data = []
        
        # Convert all pixels to SPI data
        for r, g, b in self.pixels:
            spi_data.extend(self._rgb_to_spi(r, g, b))
        
        # Add reset signal (zeros)
        spi_data.extend([0x00] * 80)  # >=50us reset pulse
        
        # Send data
        self.spi.transfer(spi_data)
        time.sleep(0.001)  # Small delay
    
    def set_pixel(self, index, r, g, b):
        """Set individual pixel color"""
        if 0 <= index < self.num_pixels:
            self.pixels[index] = (r, g, b)
    
    def fill(self, r, g, b):
        """Fill all pixels with the same color"""
        for i in range(self.num_pixels):
            self.pixels[i] = (r, g, b)
    
    def show(self):
        """Update the physical strip with current pixel values"""
        self._update_strip()

    def all_on(self):
        for i in range(self.num_pixels):
            if i < 6:
                self.set_pixel(i, 0, self.side_value, 0)
            elif i > 23:
                self.set_pixel(i, self.side_value, 0, 0)
            else:
                self.set_pixel(i, 255, 255, 255)
        self.show()
    
    def side_on(self):
        for i in range(self.num_pixels):
            if i < 6:
                self.set_pixel(i, 0, self.side_value, 0)
            elif i > 23:
                self.set_pixel(i, self.side_value, 0, 0)
            else:
                self.set_pixel(i, 0, 0, 0)
        self.show()
    
    def headlights_off(self):
        for i in range(self.num_pixels):
            if i > 5 and i < 24:
                self.set_pixel(i, 0, 0, 0)
        self.show()

    def headlights_on(self):
        for i in range(self.num_pixels):
            if i > 5 and i < 24:
                self.set_pixel(i, 255, 255, 255)
        self.show()
    
    def off(self):
        self.fill(0, 0, 0)
        self.show()
    
    def cleanup(self):
        """Clean up SPI resources"""
        self.off()
        self.spi.close()