
import time
from gy271_compass import CompassError, GY271Compass


def main() -> None:
	try:
		compass = GY271Compass(
			bus_number=7,
			# address=None auto-scans: 0x2C, 0x0D, 0x1E
			address=None,
			declination_deg=0.0,
			x_offset=0.0,
			y_offset=0.0,
		)
	except CompassError as e:
		print(f"Compass init failed: {e}")
		return
	except Exception as e:
		print(f"Unexpected init error: {e}")
		return

	print(
		f"Compass online | bus={compass.bus_number} addr={hex(compass.address)} protocol={compass.protocol}"
	)
	print("Press Ctrl+C to stop")

	try:
		while True:
			sample = compass.read()
			print(
				f"Heading={sample['heading']:6.1f} deg | "
				f"x={sample['x']:8.0f} y={sample['y']:8.0f} z={sample['z']:8.0f}"
			)
			time.sleep(0.2)
	except KeyboardInterrupt:
		print("Stopped")
	except Exception as e:
		print(f"Read failed: {e}")


if __name__ == "__main__":
	main()