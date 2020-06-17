from osmread import parse_file, Way, Node
from collections import defaultdict
import heapq

from queue import PriorityQueue
import math

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True, init=True)
class WNode:
    weight: float
    distance: float = field(compare=False)
    node: Node = field(compare=False)
    prev: Any = field(compare=False)
    way: Any = field(compare=False)


NVS_LAT, NVS_LON = 45.2551338, 19.8451756
HVSINE = math.cos(math.radians(NVS_LAT))

DEG_RADIUS = math.radians(6371)

ALLOWED_ROADS = [
    'motorway',
    'trunk',
    'primary',
    'secondary',
    'tertiary',
    'unclassified',
    'residential',
    'motorway_link',
    'trunk_link',
    'primary_link',
    'secondary_link',
    'tertiary_link',
    'living_street'
]

SPEEDS = {
    'motorway' : 10,
    'trunk' : 10,
    'primary' : 10,
    'secondary' : 9,
    'tertiary' : 8,
    'unclassified' : 7,
    'residential' : 6,
    'motorway_link' : 9,
    'trunk_link' : 8,
    'primary_link' : 7,
    'secondary_link' : 6,
    'tertiary_link' : 5,
    'living_street' : 4
}

nodes = set()
link_count = 0

node_neighbors = defaultdict(lambda: [])

node_dict = {}

important_ways = []

def draw_path(plt, path, *args, **kwargs):
    plt.plot([p.lon for p in path], [p.lat for p in path], *args, **kwargs)

def draw_dumb_map(plt):
    for w in important_ways:
        draw_path(plt, [node_dict[n] for n in w.nodes], lw=SPEEDS[w.tags['highway']] / 10.0, c='gray')

def load():
    num_links = 0
    for entity in parse_file('novi_sad.osm.pbf'):
        if isinstance(entity, Node):
            node_dict[entity.id] = entity
        elif isinstance(entity, Way) and 'highway' in entity.tags and entity.tags['highway'] in ALLOWED_ROADS:
            important_ways.append(entity)
            nodes.update(set(entity.nodes))
            for i, cur in enumerate(entity.nodes[1:]):
                prev = entity.nodes[i]
                node_neighbors[prev].append((cur, entity))
                if 'oneway' not in entity.tags or entity.tags['oneway'] == 'no':
                    node_neighbors[cur].append((prev, entity))
                num_links += 1

    print('nodes:', len(nodes))
    print('links:', num_links)


start = 1229948886 #2918444603
target = 6793137685 #2317759012


def get_expected_speed(way):
    return SPEEDS[way.tags['highway']]


def distance(a, b, way=None, use_speed=False):
    x = (a.lon - b.lon) * HVSINE
    y = a.lat - b.lat
    speed = 1 if not use_speed else get_expected_speed(way)
    return math.sqrt(x*x + y*y) / speed


def create_path(item):
    r = []
    while item:
        r.append(item.node)
        # if item.way:
        #     print(item.way.tags.get('name', ' ?? '))
        item = item.prev
    r.reverse()
    return r


def pathfind(start, target, use_speed=False):

    start_node = node_dict[start]
    swnode = WNode(1, 0, start_node, None, None)
    target_node = node_dict[target]
    q = [swnode]

    visited = {start}
    inserted = {start: swnode}

    counted = 0

    while q:
        item: WNode = heapq.heappop(q)
        counted += 1

        print(f' search: {counted} | {item.distance * DEG_RADIUS} | {item.distance / item.weight * 100:4.1f}%', end='\r')

        visited.add(item.node.id)

        if item.node.id == target:
            return create_path(item), item.distance

        for neigh, way in node_neighbors[item.node.id]:
            # print(item.node, '->', neigh, ' ~> ' , way.tags.get('name', ' ?? '))
            if neigh in visited:
                continue

            if neigh in inserted:
                wnode = inserted[neigh]
                dist = item.distance + distance(item.node, wnode.node, way, use_speed)
                if dist < wnode.distance:
                    wnode.distance = dist
                    wnode.weight = dist + distance(wnode.node, target_node, way, use_speed)
                    wnode.prev = item
                    heapq.heapify(q) # re-heapify
            else:
                neigh_node = node_dict[neigh]
                dist = item.distance + distance(item.node, neigh_node, way, use_speed)
                weight = dist + distance(neigh_node, target_node, way, use_speed)
                wnode = WNode(weight, dist, neigh_node, item, way)
                inserted[neigh] = wnode
                heapq.heappush(q, wnode)

    return None, None
