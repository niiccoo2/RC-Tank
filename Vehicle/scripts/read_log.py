start_time: float = 0
end_time: float = 0

with open("./tank.log", "r") as f:
  for line in f:
    if "Time to fix" in line:
      split_line = line.split(" ")
      print(split_line[-1]) # last line
    
