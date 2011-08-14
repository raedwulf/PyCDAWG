#!/usr/bin/python
# -*- coding: utf-8 -*-

import pydot

# Node class.
class Node:

    sid_count = 0

    def __init__(self, id='', a=None):
        if a != None and isinstance(a, Node):
            self.len = a.len
            self.suf = a.suf
            self.to = a.to
        else:
            self.len = 0
            self.suf = None
            self.to = {}
        if id != '':
            self.id = id
        else:
            self.id = 's' + str(Node.sid_count)
            Node.sid_count += 1

# Edge class.
class Edge:

    def __init__(
        self,
        src,
        substr,
        dst,
        ):
        self.src = src
        self.substr = substr
        self.dst = dst


def cdawg(w):

    def update(s, (k, p)):
        # (s, (k, p - 1)) is the canonical reference pair for the active point.
        c = w[p]
        oldr = None
        s1 = None
        while not check_end_point(s, (k, p - 1), c):
            if k <= p - 1:  # Implicit case.
                if s1 == extension(s, (k, p - 1)):
                    redirect_edge(s, (k, p - 1), r)
                    (s, k) = canonize(s.suf, (k, p - 1))
                    continue
                else:
                    s1 = extension(s, (k, p - 1))
                    r = split_edge(s, (k, p - 1))
            else:
                r = s # Explicit case.
            r.to[w[p]] = ((p, e), sink)
            if oldr != None:
                oldr.suf = r
            oldr = r
            (s, k) = canonize(s.suf, (k, p - 1))
        if oldr != None:
            oldr.suf = s
        return separate_node(s, (k, p))

    def extension(s, (k, p)):
        # (s, (k, p)) is a canonical reference pair.
        if k > p:
            return s
        return s.to[w[k]][1]

    def redirect_edge(s, (k, p), r):
        (k1, p1) = s.to[w[k]][0]
        s.to[w[k1]] = ((k1, k1 + p - k), r)

    def split_edge(s, (k, p)):
        # Let (s, (k1, p1), s1) be the w[k]-edge from s.
        ((k1, p1), s1) = s.to[w[k]]
        r = Node()
        # Replace the edge by edges (s, (k1, k1 + p - k), r) and
        # (r, (k1 + p - k + 1, p1), s1).
        s.to[w[k1]] = ((k1, k1 + p - k), r)
        r.to[w[k1 + p - k + 1]] = ((k1 + p - k + 1, p1), s1)
        r.len = s.len + p - k + 1
        return r

    def separate_node(s, (k, p)):
        (s1, k1) = canonize(s, (k, p))
        # Implicit case.
        if k1 <= p:
            return (s1, k1)
        # Explicit case.
        if s1.len == s.len + p - k + 1:  # Solid case.
            return (s1, k1)

        # Non-solid case.
        # Create node r1 as a duplication of s1, together with the out-going
        # edges of s1
        r1 = Node(s1)
        r1.suf = s1.suf
        s1.suf = r1
        r1.len = s.len + p - k + 1
        while True:
            # Replace the w[k]-edge from s to s1 by edge (s, (k, p), r1)
            s.to[w[k]] = ((k, p), r1)
            (s, k) = canonize(s.suf, (k, p - 1))
            if (s1, k1) != canonize(s, (k, p)):
                break
        return (r1, p + 1)

    def check_end_point(s, (k, p), c):
        if k <= p:  # Implicit case.
            ((k1, p1), s1) = s.to[w[k]]
            return c == w[k1 + p - k + 1]
        else:
            return c in s.to

    def canonize(s, (k, p)):
        if k > p:
            return (s, k)
        ((k1, p1), s1) = s.to[w[k]]
        while p1 - k1 <= p - k:
            k = k + p1 - k1 + 1
            s = s1
            if k <= p:
                ((k1, p1), s1) = s.to[w[k]]
        return (s, k)

    m = len(w)

    # Create the nodes source, sink and _|_.
    source = Node(id='source')
    sink = Node(id='sink')
    bt = Node(id='root')
    for j in range(1, m):
        # Create a new edge (_|_, (-j, -j), source).
        bt.to[w[-j]] = ((-j, -j), source)
        #bt.to[w[j]] = ((j, j), source)

    source.suf = bt
    source.len = 0
    bt.len = -1
    e = len(w)
    sink.len = e
    (s, k) = (source, 0)
    i = 0
    while True:
        (s, k) = update(s, (k, i))
        if w[i] == '$':
            break
        i = i + 1
    return bt


if __name__ == '__main__':
    word = 'cocoa$'
    root = cdawg(word)

    graph = pydot.Dot(graph_type='digraph')
    node_root = pydot.Node('root')
    graph.add_node(node_root)
    nodes = {'root': node_root}


    def traverse_nodes(n):
        for (k, v) in n.to.items():
            need_traverse = False
            if v[1].id in nodes:
                node = nodes[v[1].id]
            else:
                node = nodes[v[1].id] = pydot.Node(v[1].id)
                graph.add_node(node)
                need_traverse = True
            if v[0][0] >= 0:
                l = word[v[0][0]:v[0][1] + 1]
            else:
                l = word[v[0][0] - 1:v[0][1]]
            graph.add_edge(pydot.Edge(nodes[n.id], node, label=l,
                           style='solid'))
            if need_traverse:
                traverse_nodes(v[1])
        if n.suf:
            graph.add_edge(pydot.Edge(nodes[n.id], nodes[n.suf.id],
                           style='dashed'))


    traverse_nodes(root)
    graph.write_png('out.png')