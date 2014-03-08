"""
Graph data structure
"""
from collections import Mapping

import unittest

class Graph(Mapping):
    """
    create a graph data structure
    """
    def __init__(self, coll=None):
        """create a new graph structure"""
        if coll:
            self._nodes = set(coll)
        else:
            self._nodes = set()
        self._edges = {}

    def add_node(self, node):
        """
        add a node to the graph.
        raise a KeyError if the node already exists in the graph.
        """
        if node in self._nodes:
            raise KeyError("%s already in graph" % node)
        self._nodes.add(node)

    def remove_node(self, node):
        """
        remove a node from the graph.
        raise a KeyError if the node doesn't exist in the graph.
        """
        self._nodes.remove(node)
        try:
            del self._edges[node]
        except KeyError:
            # edges are only populated when connections are made,
            # so this is not an error
            pass
        for key in self.nodes:
            try:
                self._edges[key].remove(node)
            except (KeyError, IndexError):
                pass
    @property
    def nodes(self):
        """return a list of nodes"""
        return list(self._nodes)

    def node_edges(self, node):
        """return a list of connections to node"""
        edges = self._edges.get(node)
        if not edges:
            edges = []
        return list(edges)

    def connect(self, node1, node2):
        """
        connect two nodes such that
        node1 --> node2
        raises KeyError if either node isn't in the graph
        """
        if node1 not in self:
            raise KeyError(node1)
        if node2 not in self:
            raise KeyError(node2)
        edges = self._edges.get(node1, None)
        if not edges:
            edges = set()
        edges.add(node2)
        self._edges[node1] = edges

    def disconnect(self, node1, node2):
        """
        disconnect two nodes.
        Raises KeyError if the nodes aren't currently connected
        """
        self._edges[node1].remove(node2)

    def path_to(self, node1, node2):
        """
        return the path from node1 to node2.
        Raises KeyError if the nodes aren't connected
        """
        def trace_back(start, end, backtrace):
            """go from start to end using backtrace"""
            traces = [end]
            node = end
            while start not in traces:
                traces.append(backtrace[node])
                node = backtrace[node]
            return list(reversed(traces))
        backtrace = dict()              # breadcrumbs
        to_traverse = set([node1])      # nodes we haven't checked yet
        traversed = set()               # nodes we've checked
        # walk graph from node1, populating a backtrace until node2 is present
        # in the backtrace (a path has been found)
        while node2 not in traversed:
            discovered = set()
            for node in to_traverse:
                # find all nodes connected to the current node that we
                # haven't traversed yet
                edges = set(self.node_edges(node)).difference(traversed)
                for each in edges:
                    # Add each connected node that we haven't seen yet
                    # to the backtrace like so: {node: previous}
                    backtrace[each] = node
                discovered.update(edges)
            if not discovered:
                raise KeyError("%s not connected to %s" % (node1, node2))
            # add discovered instead of to_traverse to traversed here.
            # This simplifies the code a bit
            traversed.update(discovered)
            to_traverse = discovered
        return trace_back(node1, node2, backtrace)

    def reverse(self):
        """
        Returns a new Graph with edge directions reversed
        a --> b     <==>    b --> a
        """
        graph = Graph(self.nodes)
        for key, values in self.iteritems():
            for val in values:
                graph.connect(val, key)
        return graph

    def __getitem__(self, key):
        if key not in self.nodes:
            raise KeyError(key)
        else:
            return self.node_edges(key)

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)


# disable the 'too many class methods' from unittest.TestCase
# pylint: disable=R0904

class GraphTests(unittest.TestCase):
    """tests for the Graph class"""
    def test_mapping(self):
        """test the mapping interface"""
        graph = Graph(range(1, 4))
        graph.connect(1, 2)
        self.failUnless(graph[1] == [2])
        graph.connect(2, 3)
        self.failUnless(graph.items() == [(1, [2]), (2, [3]), (3, [])])
    def test_path_to(self):
        """test path_to method"""
        graph = Graph(range(5))
        for nodes in zip(range(1, 4), range(2, 5)):
            graph.connect(nodes[0], nodes[1])
        self.failUnless(graph.path_to(1, 4) == [1, 2, 3, 4])
    def test_add_remove(self):
        """test adding and removing"""
        graph = Graph()
        graph.add_node(1)
        # Trying to connect to nonexistant node
        self.assertRaises(KeyError, graph.connect, 1, 2)
        self.assertRaises(KeyError, graph.connect, 2, 1)
        # Connecting to a valid node
        graph.add_node(2)
        graph.connect(1, 2)
        self.failUnless(graph[1] == [2])
        # Removal behavior
        graph.remove_node(2)
        self.failUnless(graph[1] == [])
        # Can't remove again
        self.assertRaises(KeyError, graph.remove_node, 2)
    def test_reverse(self):
        """test the reverse method"""
        graph = Graph(range(5))
        for nodes in zip(range(1, 4), range(2, 5)):
            graph.connect(nodes[0], nodes[1])
        graph = graph.reverse()
        self.failUnless(graph.path_to(4, 1) == [4, 3, 2, 1])



if __name__ == '__main__':
    unittest.main()

# EOF
