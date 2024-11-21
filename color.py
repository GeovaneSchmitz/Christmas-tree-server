import colorsys
import json
import random

color_count = 32


def color_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


colors = []

for i in range(color_count):
    r_int = int(i / 31 * 255)
    g_int = int(i / 31 * 255)
    b_int = int(i / 31 * 255)
    colors.append(color_to_hex(r_int, g_int, b_int))
random.shuffle(colors)
print(json.dumps(colors))


colors = []
for i in range(color_count):
    r, g, b = colorsys.hsv_to_rgb(i / (color_count - 1), 1.0, 1.0)

    r_int = int(r * 255)
    g_int = int(g * 255)
    b_int = int(b * 255)

    colors.append(color_to_hex(r_int, g_int, b_int))
print(json.dumps(colors))


color_count_step = 4
step_count_total = 256
max_number = 255
steps = []
step_per_color = step_count_total // color_count_step
for i in range(step_per_color // 2):
    steps.append(int(i / ((step_per_color // 2) - 1) * max_number))
for i in range(step_per_color // 2):
    steps.append(max_number - int(i / ((step_per_color // 2) - 1) * max_number))
for i in range(color_count_step - 1):
    for j in range(step_per_color):
        steps.append(0)

print(steps)