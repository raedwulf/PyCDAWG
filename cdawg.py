#!/usr/bin/env python2

"""
PyCDAWG 0.0.0
Copyright (C) 2011 by Tai Chi Minh Ralph Eastwood
v

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys
import pygraphviz

# Node class.
class Node:

    sid_count = 0

    def __init__(self, id='', n=None):
        if n != None and isinstance(n, Node):
            self.len = n.len
            self.suf = n.suf
            self.to = n.to
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

    def __init__(self, src, substr, dst):
        self.src = src
        self.substr = substr
        self.dst = dst


def cdawg(ws):

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
            r.to[w[p]] = ((p, e[j]), sink)
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
        r1 = Node(n=s1)
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

    # Keep track of all of the lengths of each subword.
    w = ''
    m = j = 0
    e = []
    for _w in ws:
        j += 1
        w += _w + unichr(255 + j)
        e.append(m + len(_w))
        m = len(w)

    # Create the nodes source, sink and _|_.
    source = Node(id='source')
    bt = Node(id='root')
    for j in range(0, m):
        # Create a new edge (_|_, (-j, -j), source).
        #bt.to[w[-j]] = ((-j, -j), source)
        bt.to[w[j]] = ((j, j), source)

    source.suf = bt
    source.len = 0
    bt.len = -1

    (s, k) = (source, 0)
    i = j = 0
    while i < len(w):
        # Create a new sink.
        sink = Node(id='sink' + str(j))
        sink.length = e[j]
        while True:
            (s, k) = update(s, (k, i))
            if i == e[j]:
                break
            i += 1
        i += 1
        j += 1
    return w, bt


if __name__ == '__main__':
    word, root = cdawg(sys.argv[1:])

    graph = pygraphviz.AGraph(strict=False,directed=True)
    graph.node_attr['fontname'] = 'Sans 12'
    graph.edge_attr['fontname'] = 'Sans 12'
    graph.graph_attr['fontname'] = 'Sans 12'
    graph.add_node('root')
    nodes = ['root']
    internal_nodes = [root]

    def translate_label(l):
        # replace the label with something more readable
        label = ''
        for c in l:
            uc = ord(c)
            if uc < 256:
                label += c
            else:
                ucn = uc - 256
                ln = ''
                while True:
                    ln = unichr(0x2080 + (ucn % 10)) + ln
                    ucn /= 10
                    if ucn == 0:
                        break
                label += '$' + ln
        return label

    def traverse_nodes(n):
        for (k, v) in n.to.items():
            need_traverse = False
            # check if node needs creating
            node = v[1].id
            if v[1].id not in nodes:
                nodes.append(node)
                internal_nodes.append(v[1])
                graph.add_node(node)
                need_traverse = True
            # get the label
            if v[0][0] >= 0:
                l = word[v[0][0]:v[0][1] + 1]
            else:
                l = word[v[0][0] - 1:v[0][1]]
            # add the edge
            graph.add_edge(n.id, node, l, label=translate_label(l),
                           style='solid')
            if need_traverse:
                traverse_nodes(v[1])

    traverse_nodes(root)

    for n in internal_nodes:
        print n.id
        if n.suf:
            graph.add_edge(n.id, n.suf.id,
                           style='dashed')

    graph.layout(prog='dot')
    graph.draw('out.png')
