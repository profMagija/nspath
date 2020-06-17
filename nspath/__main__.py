from nspath import *
import random
from smopy import Map

import matplotlib.pyplot as plt

load()

def calc_dist(path):
    return sum(map(lambda x: distance(x[0], x[1]), zip(path[1:], path[:-1])))

while True:
    start = int(input(f'start [{start}]: ') or start)
    target = int(input(f'target [{target}]: ') or target)
    res, dist = pathfind(start, target)
    print()
    res2, _ = pathfind(start, target, True)
    print()

    print(dist * DEG_RADIUS)
    print(calc_dist(res2) * DEG_RADIUS)

    ax = plt.subplot(111)
    ax.set_aspect(1 / HVSINE)
    draw_dumb_map(plt)
    draw_path(plt, res)
    draw_path(plt, res2)
    plt.show()

nds = list(nodes)
max_percent = 0
while True:
    start = random.choice(nds)
    target = random.choice(nds)
    res, dist = pathfind(start, target, False)
    print()

    if res is None:
        continue

    res2, _ = pathfind (start, target, True)
    print()

    dist2 = sum(map(lambda x: distance(x[0], x[1]), zip(res2[1:], res2[:-1])))

    dist *= DEG_RADIUS * 1000
    dist2 *= DEG_RADIUS * 1000


    percent = 2 * (dist2 - dist) / (dist2 + dist)
    if percent > max_percent:
        print(f'{start} -> {target} {dist:.2f} {dist2:.2f} {dist2 - dist:.2f} {percent:.2f}%')
        max_percent = percent