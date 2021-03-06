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
            # Should ye be copied?
            self.from_ = copy(n.from_)
            self.credit = n.credit
        else:
            self.len = 0
            self.suf = None
            self.to = {}
            self.from_ = []
            self.credit = False
        if id != '':
            self.id = id
        else:
            self.id = 's' + str(node.sid_count)
            node.sid_count += 1

    #def __repr__(self):
        #return "(id = %s, len = %s, suffix = %s, edges = %s)" % (self.id, self.len, self.suf, self.to)

    def __repr__(self):
        return self.id

    def edge(self, c, (k, p), n):
        self.to[c] = ((k, p), n)
        n.from_.append((c, self))

# Cdawg class
class slidingcdawg:
    def __init__(self, debug = False):

        # Debug mode
        self.debug = debug

        # Create the nodes source, sink and _|_.
        self.source = node(id='source')
        self.bt = node(id='root')

        self.source.suf = self.bt
        self.source.len = 0
        self.bt.len = -1

        self.sk = (self.source, 0)
        self.i = 0
        self.e = 4294967296
        self.w = ''

        # Create a new sink.
        self.sink = node(id='sink')
        self.sink.length = self.e

    def __extension(self, s, (k, p)):
        # (s, (k, p)) is a canonical reference pair.
        if k > p:
            return s
        return s.to[self.w[k]][1]

    def __redirect_edge(self, s, (k, p), r):
        (k1, p1) = s.to[self.w[k]][0]
        s.edge(self.w[k1], (k1, k1 + p - k), r)

    def __split_edge(self, s, (k, p)):
        # Let (s, (k1, p1), s1) be the w[k]-edge from s.
        ((k1, p1), s1) = s.to[self.w[k]]
        r = node()
        # Replace the edge by edges (s, (k1, k1 + p - k), r) and
        # (r, (k1 + p - k + 1, p1), s1).
        s.edge(self.w[k1], (k1, k1 + p - k), r)
        r.edge(self.w[k1 + p - k + 1], (k1 + p - k + 1, p1), s1)
        r.len = s.len + p - k + 1
        # The edge we are splitting is where the deletion point is
        (s2, (k2, p2)) = self.dp
        if s == s2 and self.w[k] == self.w[k2]:
            self.dp = (r, (k, r.len))
        return r

    def __separate_node(self, s, (k, p)):
        (s1, k1) = self.__canonize(s, (k, p))
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
            s.edge(self.w[k], (k, p), r1)
            (s, k) = self.__canonize(s.suf, (k, p - 1))
            if (s1, k1) != self.__canonize(s, (k, p)):
                break
        return (r1, p + 1)

    def __check_end_point(self, s, (k, p), c):
        if k <= p:  # Implicit case.
            ((k1, p1), s1) = s.to[self.w[k]]
            return c == self.w[k1 + p - k + 1]
        else:
            return c in s.to

    def __canonize(self, s, (k, p)):
        if k > p:
            return (s, k)
        ((k1, p1), s1) = s.to[self.w[k]]
        while p1 - k1 <= p - k:
            k = k + p1 - k1 + 1
            s = s1
            if k <= p:
                ((k1, p1), s1) = s.to[self.w[k]]
        return (s, k)

    def __update(self, s, (k, p)):
        w = self.w
        e = self.e
        sink = self.sink

        # Deletion point.
        if len(w) == 1:
            self.dp = (self.source, (0, 0))
        else:
            (s1, (k1, p1)) = self.dp
            p1 += 1
            self.dp = (s1, (k1, p1))

        # (s, (k, p - 1)) is the canonical reference pair for the active point.
        c = w[p]
        oldr = None
        s1 = None
        while not self.__check_end_point(s, (k, p - 1), c):
            if k <= p - 1:  # Implicit case.
                if s1 == self.__extension(s, (k, p - 1)):
                    self.__redirect_edge(s, (k, p - 1), r)
                    (s, k) = self.__canonize(s.suf, (k, p - 1))
                    continue
                else:
                    s1 = self.__extension(s, (k, p - 1))
                    r = self.__split_edge(s, (k, p - 1))
            else:
                r = s # Explicit case.
            r.edge(w[p], (p, self.e), sink)
            if oldr != None:
                oldr.suf = r
            oldr = r
            (s, k) = self.__canonize(s.suf, (k, p - 1))
        if oldr != None:
            oldr.suf = s
        return self.__separate_node(s, (k, p))

    def __find(self, k):
        def traverse_nodes(n, key, i, nl):
            for (c, ((k, p), n1)) in n.to.items():
                if c == key[i]:
                    nl.append((n, c))
                    if self.w[k:p].startswith(key[i:i+p-k]):
                        if len(key) <= i + p - k:
                            return nl
                        else:
                            traverse_nodes(n1, key, i+p-k, nl)
                    else:
                        return None
        return traverse_nodes(self.source, k, 0, [])

    def __getitem__(self, s):
        return self.__find(s)

    def add(self, c):
        # Add a new character
        self.w += c
        # Create a new edge (_|_, (i, i), source)
        if c not in self.bt.to:
            self.bt.edge(c, (self.i, self.i), self.source)
        (s, k) = self.sk
        self.sk = self.__update(s, (k, self.i))
        self.i += 1
        # If debugging, render after every character.
        if self.debug:
            self.render('out_' + self.w + '.png')
        print self.dp

    def delete(self):
        # Get the deletion point.
        (s, (k, p)) = self.dp
        cp = k
        #if s == root:
            #cp += 1
        # Update the delete point
        self.dp = self.__canonize(s.suf, (cp, p))
        # Need to shorten (active point on backbone).
        if self.sk[1] <= self.i - 1 and self.sk[0] == s and self.w[self.sk[1]] == self.w[k]:
            # Shorten the path
            ((k1, p1), s1) = s.to[self.w[k]]
            s.to[self.w[k]] = ((self.sk[1], p1), s1)
            # Update the active point
            if self.sk[0] == self.source:
                self.sk = (self.source, self.sk[1] + 1)
            else:
                self.sk = self.__canonize(self.sk[0].suf, (self.sk[1], self.i - 1))
        else: # Need to delete an edge.
            # Delete the offending edge
            del s.to[self.w[k]]
            # Out-degree == 1 and parent ain't root
            if len(s.to) == 1 and s != self.bt:
                # Get the last edge and delete it
                (kl, pl), sl = s.to[s.to.keys()[0]]
                del s.to[s.to.keys()[0]]
                # Update the length
                length = sl.len
                # Update labels and ends
                for c, n in s.from_:
                    if self.sk[0] == n:
                        (kt, pt), st = n.to[c]
                        self.sk = (n, self.sk[1] - pt - kt + 1)
                    # FIXME: Somehow redirect?
                    ((k1, p1), s1) = n.to[c]
                    n.edge(c, (k1, pl), sl)
                # Delete this node
                del s
            elif len(self.w) == 1:
                s.to = {}
            else:
                print "delete broken...."
        if self.debug:
            self.render('out_' + self.w + '_.png')

    def render(self, outfile):
        import pygraphviz

        word = self.w
        root = self.bt

        # Create the graph.
        graph = pygraphviz.AGraph(strict=False,directed=True)
        graph.node_attr['fontname'] = 'Sans 12'
        graph.edge_attr['fontname'] = 'Sans 12'
        graph.graph_attr['fontname'] = 'Sans 12'
        graph.add_node(unichr(0x22a5))
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
                if n.suf.id == 'root':
                    end = unichr(0x22a5)
                else:
                    end = n.suf.id
                graph.add_edge(n.id, end,
                               style='dashed')

        # Layout & draw the graph.
        graph.layout(prog='dot')
        graph.draw(outfile)

if __name__ == '__main__':
    import sys

    # Concatenate the input words and separate using unique symbols.
    c = slidingcdawg(debug=True)
    for w in sys.argv[1]:
        c.add(w)

    c.delete()
