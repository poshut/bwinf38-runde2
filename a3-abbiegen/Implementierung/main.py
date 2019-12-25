import sys
import math
import queue
import numpy as np
import collections
import itertools

JUNCTIONS = {
    0: (0,0),
    1: (1,0),
    2: (2,0),
    3: (3,0),
    4: (4,0),

    5: (0,1),
    6: (2,1),

    7: (0,2),
    8: (1,2),

    9: (0,3),
}

SOURCE = 9
TARGET = 4

ROADS = {
    0: {1,5},
    1: {0,2,5,6},
    2: {1,3,6},
    3: {2,4,6},
    4: {3},

    5: {0,1,7,8},
    6: {1,2,3,8},

    7: {5,8,9},
    8: {7,5,6},

    9: {7},
}

FLOAT_ERROR_DIGITS = 8
TURN_PRIO = 999999

def straight(p1, junc, p2):
    delta1_x = junc[0] - p1[0]
    delta1_y = junc[1] - p1[1]
    delta_1 = distance(p1, junc)

    delta2_x = p2[0] - junc[0]
    delta2_y = p2[1] - junc[1]
    delta_2 = distance(p2, junc)

    return abs(round((delta1_x*delta2_x+delta1_y*delta2_y)/(delta_1*delta_2), FLOAT_ERROR_DIGITS))==1

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def format_roadnode(j1, j2):
    if j1 < j2:
        return '{}_{}'.format(j1, j2)
    return '{}_{}'.format(j2, j1)

def get_roadnode(n):
    return tuple(map(int, n.split("_")))

def build_graph(junctions, roads, source_junction, target_junction):
    nodes = dict()
    edges = collections.defaultdict(set)

    for source in ROADS:
        for target in ROADS[source]:
            nodes[format_roadnode(source, target)] = distance(junctions[source], junctions[target])
    
    for junction in JUNCTIONS:
        for comb in itertools.combinations(ROADS[junction], 2):
            pos0 = JUNCTIONS[comb[0]]
            posj = JUNCTIONS[junction]
            pos1 = JUNCTIONS[comb[1]]
            s = straight(pos0, posj, pos1)
            r0 = format_roadnode(comb[0], junction)
            r1 = format_roadnode(comb[1], junction)
            edges[r0].add((r1, s))
            edges[r1].add((r0, s))
    

    sources = set()
    for next_junction in ROADS[source_junction]:
        sources.add(format_roadnode(source_junction, next_junction))
    
    targets = set()
    for last_junction in ROADS[target_junction]:
        targets.add(format_roadnode(target_junction, last_junction))


    return nodes, edges, sources, targets

def dijkstra(nodes, edges, sources, targets, number_turns=None):
    pq = queue.PriorityQueue()
    for source in sources:
        pq.put((nodes[source], source, [source], 0))

    discovered = set()
    
    while True:
        if pq.empty():
            exit("queue empty! there seems to be no route to the target node!")
        prio, node, prev, turns = pq.get()
        if node in discovered:
            continue

        discovered.add(node)
        for edge in edges[node]:
            prio_new = prio + nodes[edge[0]]
            if not edge[1]:
                if turns == number_turns:
                    prio_new += TURN_PRIO

            pq.put((prio_new, edge[0], prev + [edge[0]], turns + (1 if not edge[1] else 0)))

        if node in targets:
            break

    distance = 0
    for step in prev:
        distance += nodes[step]
    
    if number_turns is not None and turns != number_turns:
        return None, None, None

    return prev, distance, turns


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage", sys.argv[0], "<tolerance (percent)>", file=sys.stderr)
        exit(1)
    
    try:
        TOLERANCE = int(sys.argv[1])
    except ValueError:
        print("Usage", sys.argv[0], "<tolerance (percent)>", file=sys.stderr)
        exit(1)


    nodes, edges, sources, targets = build_graph(JUNCTIONS, ROADS, SOURCE, TARGET)
    min_path, min_distance, max_turns = dijkstra(nodes, edges, sources, targets)

    less_turns = 0
    while True:
        path, distance, turns = dijkstra(nodes, edges, sources, targets, number_turns=max_turns-less_turns)

        if path is None or distance > min_distance * (1 + TOLERANCE/100):
            break

        # print(' -> '.join(path))
        # print("Distance", distance)
        # print(turns, "turns")
        # print()
        res_path, res_distance, res_turns = path, distance, turns
        less_turns += 1

    junctions = [SOURCE]
    for road in res_path:
        j1, j2 = get_roadnode(road)
        if junctions[-1] == j1:
            junctions.append(j2)
        else:
            junctions.append(j1)

    print("Distance", round(res_distance, 2))

    if res_turns == 1:
        print(res_turns, "turn")
    else:
        print(res_turns, "turns")
    print(' -> '.join(map(str, junctions)))
