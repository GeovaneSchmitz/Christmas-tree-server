import colorsys
import json
import random
import math
step_count = 256
min_value = 0
max_value = 255
steps = []
for i in range(step_count):
    steps.append(int(min_value + math.sin(i * math.pi / step_count) * (max_value - min_value)))
print(steps)