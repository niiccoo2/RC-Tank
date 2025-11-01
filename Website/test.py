def convert_car_to_tracks(trottle: float, stick: float):
    left: float = trottle
    right: float = trottle

    left = trottle+(.2*stick)
    right = trottle-(.2*stick)

    if left > 1.00:
        left = 1.00
    if right > 1.00:
        right = 1.00
    
    return left, right
    

while True:
    left, right = convert_car_to_tracks(float(input("Throttle: ")), stick = float(input("Stick: ")))

    print(f"Left: {left} Right: {right}")