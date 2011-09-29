#!/usr/bin/env python2

"""
PyCDAWG 0.0.0
Copyright (C) 2011 by Tai Chi Minh Ralph Eastwood

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

from copy import copy

# Node class.
class node:

    sid_count = 0

    def __init__(self, id='', n=None):
        if n != None and isinstance(n, node):
            self.len = n.len
            self.suf = n.suf
            self.to = copy(n.to)
        else:
            self.len = 0
            self.suf = None
            self.to = {}
        if id != '':
            self.id = id
        else:
            self.id = 's' + str(node.sid_count)
            node.sid_count += 1

# Cdawg class
class cdawg:
    def __init__(self):
        # Create the nodes source, sink and _|_.
        self.source = node(id='source')
        self.bt = node(id='root')

        self.source.suf = self.bt
        self.source.len = 0
        self.bt.len = -1

        self.sk = (self.source, 0)
        self.i = 0
        self.j = 0
        self.e = []
        self.w = ''
        self.values = {}

    def __update(self, s, (k, p)):
        w = self.w
        e = self.e
        j = self.j
        sink = self.sink

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
            r = node()
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
            r1 = node(n=s1)
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

    def __findend(self, k):
        def traverse_nodes(n, key, i):
            for (c, ((k, p), n1)) in n.to.items():
                if c == key[i]:
                    if key[i:i+p-k] == self.w[k:p]:
                        if len(key) == i + p - k:
                            return self.w[p]
                        else:
                            traverse_nodes(n1, key, i+p-k)
                    else:
                        return None
        return traverse_nodes(self.source, k, 0)

    def __contains__(self, k):
        return self.__findend(k) != None

    def __setitem__(self, k, v):
        # Check if the entry already exist.
        end = self.__findend(k)
        if end != None:
            self.values[end] = v
            return
        self.e.append(self.i + len(w))
        # Create a new sink.
        self.sink = node(id='sink' + str(self.j))
        self.sink.length = self.e[self.j]
        # Update new word
        self.w += w
        end = unichr(256 + self.j)
        self.w += end
        for i in range(self.i, len(self.w)):
            # Create a new edge (_|_, (-j, -j), source).
            if self.w[i] not in self.bt.to:
                self.bt.to[self.w[i]] = ((i, i), self.source)
            (s, k) = self.sk
            self.sk = self.__update(s, (k, i))
        self.i = len(self.w)
        self.j += 1
        self.values[end] = v

    def __getitem__(self, k):
        end = self.__findend(k)
        if end != None:
            return self.values[end]
        else: # TODO: Raise error instead?
            return None

    def render(self, outfile):
        import pygraphviz

        word = self.w
        root = self.bt

        # Create the graph.
        graph = pygraphviz.AGraph(strict=False,directed=True)
        graph.node_attr['fontname'] = 'Sans 12'
        graph.edge_attr['fontname'] = 'Sans 12'
        graph.graph_attr['fontname'] = 'Sans 12'
        graph.add_node('root')
        nodes = ['root']
        internal_nodes = [root]

        # Replace the label with symbol end marks with something more readable.
        def translate_label(l):
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
            root_once = False
            for (c, ((k, p), n1)) in n.to.items():
                need_traverse = False
                # Check if node needs creating.
                node = n1.id
                if n1.id not in nodes:
                    nodes.append(node)
                    internal_nodes.append(n1)
                    graph.add_node(node)
                    need_traverse = True
                # Get the label.
                l = word[k:p+1]
                # Add the edge.
                if n.id == 'root':
                    if not root_once:
                        graph.add_edge(unichr(0x22a5), node, unichr(0x03a3), label=unichr(0x03a3))
                        root_once = True
                else:
                    graph.add_edge(n.id, node, l, label=translate_label(l),
                                   style='solid')
                if need_traverse:
                    traverse_nodes(n1)

        # Recursively create nodes and edges.
        traverse_nodes(root)

        # Add the suffix links on the graph.
        for n in internal_nodes:
            if n.suf:
                graph.add_edge(n.id, n.suf.id,
                               style='dashed')

        # Layout & draw the graph.
        graph.layout(prog='dot')
        graph.draw(outfile)

if __name__ == '__main__':
    import sys

    # Concatenate the input words and separate using unique symbols.
    c = cdawg()
    for w in sys.argv[1:]:
        c[w] = "Testing 123"

    print c['hello']

    # Draw
    c.render('out.png')


