import math

coords_start: list[float] = [42.365333, -71.150556]
coords_end: list[float] = [42.388083, -71.107167]

x_diff = coords_end[0] - coords_start[0]
y_diff = coords_end[1] - coords_start[1]

bearing = math.degrees(math.atan2(y_diff, x_diff))

print(bearing)