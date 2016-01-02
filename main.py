#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re

from collections import defaultdict
from copy import deepcopy
from datetime import datetime


class Vertex(object):
    def __init__(self, v_id):
        self._id = v_id

    def __hash__(self):
        return self._id

    def __eq__(self, o):
        return self._id == o._id


class Path(object):
    def __init__(self, vertecies, graph, **kwargs):
        assert isinstance(vertecies, list)

        self._path = vertecies
        self._dist = kwargs.get("dist", None)
        self._graph = graph

    @property
    def dist(self):
        if self._dist is None:
            dist = 0
            path = self._path
            graph = self._graph
            for i, v in enumerate(path[1:]):
                last_v = path[i]
                dist += graph[last_v][v]
            self._dist = dist
        return self._dist

    @property
    def end(self):
        if len(self._path) > 0:
            return self._path[-1]
        return None

    @property
    def path(self):
        return self._path

    def add_vertex(self, v):
        last_v = self.end
        self._path.append(v)
        if last_v is None:
            self._dist = 0
        else:
            self._dist = self.dist + self._graph[last_v][v]

    def clone(self):
        return Path(self._path[:], self._graph, dist=self.dist)

    def __str__(self):
        return str(self._path)

    def __iter__(self):
        for v in self._path:
            yield v

    def __contains__(self, v):
        return v in self._path


def find_shortest_path(graph, start, end, path=None):
    path = path or Path([], graph)
    path.add_vertex(start)
    if start == end:
        return path

    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path=path.clone())
            if shortest is None or (newpath is not None and newpath.dist < shortest.dist):
                shortest = newpath
    return shortest


def create_graph(inputs):
    g = defaultdict(dict)
    for s, e, d in inputs:
        g[s][e] = g[e][s] = d
    return g


def remove_vertex(graph, vertex):
    """
    Remove a vertex from a graph and connect
    the verteces connected to that node to each other.
    """
    new_graph = deepcopy(graph)
    old_neighbors = new_graph[vertex].items()
    del new_graph[vertex]

    # Remove all references to the vertex
    for v in new_graph:
        if vertex in new_graph[v]:
            del new_graph[v][vertex]

    # Connect the old neighbors together
    for i, x in enumerate(old_neighbors):
        neighbor, dist = x
        for other_neighbor, other_dist in old_neighbors[i:]:
            if neighbor != other_neighbor:
                new_graph[neighbor][other_neighbor] = dist
    return new_graph


def main():
    start = datetime.now()
    p = re.compile("\((\d+), (\d+), (\d+)\)")
    inputs = map(lambda x: tuple(map(int, x)), p.findall(sys.stdin.readline()))
    g = create_graph(inputs)

    min_dist = float("Inf")
    min_path = None
    removed_vertex = None
    min_g = None
    for v in g:
        if v == 0 or v == len(g) - 1:
            continue
        g2 = remove_vertex(g, v)
        p = find_shortest_path(g2, 0, len(g) - 1)
        if p.dist < min_dist:
            min_dist = p.dist
            min_path = p
            removed_vertex = v
            min_g = g2
    if min_path is None:
        raise RuntimeError("Somehow could not find a minumum path whose "
                           "distance is less than infinity.")
    diff = datetime.now() - start

    for i, v in enumerate(min_path.path[1:]):
        last_v = min_path.path[i]
        # Find the skipped path
        if v not in g[last_v] or g[last_v][v] != min_g[last_v][v]:
            print("{} to {}".format(last_v, removed_vertex))
            print("{} *BLAST* to {}".format(removed_vertex, v))
        else:
            print("{} to {}".format(last_v, v))
    print("Reached Last Chance encountering {} zombie(s) in {} milliseconds."
          .format(min_path.dist, diff.microseconds / 1000))

    return 0


if __name__ == "__main__":
    sys.exit(main())
