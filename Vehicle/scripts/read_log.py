start_time: float = 0
end_time: float = 0

with open("./../tank.log", "r") as f:
  for line in f:
    if "Software started at" in line:
      split_line = line.split(" ")
      start_time = float(split_line[-1]) # last line
    elif "GPS thread started" in line:
      split_line = line.split(" ")
      end_time = float(split_line[-1]) # last line
    
    if start_time != 0 and end_time != 0:
      time_to_fix = end_time - start_time
      start_time, end_time = 0, 0
      print(time_to_fix)

