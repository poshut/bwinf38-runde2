import sys
import math
import queue
import numpy as np
import collections
import itertools
from collections import defaultdict

FLOAT_ERROR_DIGITS = 8

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

    for source in roads:
        for target in roads[source]:
            nodes[format_roadnode(source, target)] = distance(junctions[source], junctions[target])
    
    for junction in junctions:
        for comb in itertools.combinations(roads[junction], 2):
            pos0 = junctions[comb[0]]
            posj = junctions[junction]
            pos1 = junctions[comb[1]]
            s = straight(pos0, posj, pos1)
            r0 = format_roadnode(comb[0], junction)
            r1 = format_roadnode(comb[1], junction)
            edges[r0].add((r1, s))
            edges[r1].add((r0, s))
    

    sources = set()
    for next_junction in roads[source_junction]:
        sources.add(format_roadnode(source_junction, next_junction))
    
    targets = set()
    for last_junction in roads[target_junction]:
        targets.add(format_roadnode(target_junction, last_junction))


    return nodes, edges, sources, targets

def dijkstra(nodes, edges, sources, targets, number_turns=None):
    pq = queue.PriorityQueue()
    for source in sources:
        pq.put((0, source, [source], 0))

    discovered = {}
    
    while True:
        if pq.empty():
           return None, None, None
        prio, node, prev, turns = pq.get()
        if node in discovered and turns >= discovered[node]:
            continue

        discovered[node] = turns
        for edge in edges[node]:
            prio_new = prio + nodes[edge[0]]
            if not edge[1]:
                if turns == number_turns:
                    continue

            pq.put((prio_new, edge[0], prev + [edge[0]], turns + (1 if not edge[1] else 0)))

        if node in targets:
            break

    distance = 0
    for step in prev:
        distance += nodes[step]
    
    if number_turns is not None and turns != number_turns:
        return None, None, None

    return prev, distance, turns

def parse_tuple(t):
    return tuple(map(int, t.replace('(', '').replace(')', '').split(",")))

def parse_input(file):
    with open(file) as f:
        lines = f.read().split("\n")
        start_coords = parse_tuple(lines[1])
        end_coords = parse_tuple(lines[2])
        lines_roads = lines[3:]

        junctions = {}
        roads = defaultdict(set)
        junction_to_id = {}
        i = 0
        for line_road in lines_roads:
            if line_road != "":
                line_road_split = line_road.split(" ")
                a = parse_tuple(line_road_split[0])
                b = parse_tuple(line_road_split[1])
                if a not in junction_to_id:
                    junction_to_id[a] = i
                    junctions[i] = a
                    i += 1
                if b not in junction_to_id:
                    junction_to_id[b] = i
                    junctions[i] = b
                    i += 1
                id_a = junction_to_id[a]
                id_b = junction_to_id[b]
                roads[id_a].add(id_b)
                roads[id_b].add(id_a)
        start = junction_to_id[start_coords]
        end = junction_to_id[end_coords]
    return junctions, roads, start, end

def visualize(junctions, roads, start, end):
    """
    Erstelle die Datei _visualize.tex, deren Ausgabe das Netzwerk grafisch darstellt.
    """
    with open("_visualize.tex", 'w') as f:
        print("\\documentclass{standalone}\n\\usepackage{tikz}\n\\begin{document}\n\\begin{tikzpicture}", file=f)
        print("[auto=left,every node/.style={circle,fill=blue!20}]", file=f)
        for i in junctions:
            if i == start:
                print("\\node [style={fill=green!60}]", "(" + str(i) + ")", "at", junctions[i], "{" + str(i) + "};", file=f)
            elif i == end:
                print("\\node [style={fill=red!60}]", "(" + str(i) + ")", "at", junctions[i], "{" + str(i) + "};", file=f)
            else:
                print("\\node", "(" + str(i) + ")", "at", junctions[i], "{" + str(i) + "};", file=f)
        for i in roads:
            for j in roads[i]:
                print("\\draw", "(" + str(i) + ")", "--", "(" + str(j) + ");", file=f)
        print("\\end{tikzpicture}\n\\end{document}", file=f)
                
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Usage", sys.argv[0], "<filename> <tolerance (percent)>", file=sys.stderr)
        exit(1)
    
    try:
        tolerance = int(sys.argv[2])
        if tolerance < 0:
            raise ValueError
    except ValueError:
        print("Usage", sys.argv[0], "<filename> <tolerance (percent)>", file=sys.stderr)
        exit(1)


    junctions, roads, source, target = parse_input(sys.argv[1])
    visualize(junctions, roads, source, target)
    nodes, edges, sources, targets = build_graph(junctions, roads, source, target)
    min_path, min_distance, max_turns = dijkstra(nodes, edges, sources, targets)
    if min_path is None:
        print("Error: Cannot find any path from source to target in road network!")
        exit(1)

    less_turns = 0
    while True:
        path, distance, turns = dijkstra(nodes, edges, sources, targets, number_turns=max_turns-less_turns)

        if path is None or distance > min_distance * (1 + tolerance/100):
            break

        res_path, res_distance, res_turns = path, distance, turns
        less_turns += 1

    path = [source]
    for road in res_path:
        j1, j2 = get_roadnode(road)
        if path[-1] == j1:
            path.append(j2)
        else:
            path.append(j1)

    print("Distance", round(res_distance, 2))

    if res_turns == 1:
        print(res_turns, "turn")
    else:
        print(res_turns, "turns")
    print(' -> '.join(map(lambda j: str(junctions[j]), path)))
