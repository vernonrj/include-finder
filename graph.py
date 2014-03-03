"""
Graph data structure
"""
from collections import Mapping

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
        backtrace = dict()
        next_traverse = set([node1])
        while True:
            traversed = set(backtrace.keys())
            edges = set()
            for node in next_traverse:
                new_edges = set(self.node_edges(node))
                new_edges.difference_update(traversed)
                for each in new_edges:
                    backtrace[each] = node
                edges.update(new_edges)
            if not edges:
                raise KeyError("%s not connected to %s" % (node1, node2))
            if node2 in edges:
                return trace_back(node1, node2, backtrace)
            next_traverse = edges
    def __getitem__(self, key):
        if key not in self.nodes:
            raise KeyError(key)
        else:
            return self.node_edges(key)
    def __iter__(self):
        return iter(self.nodes)
    def __len__(self):
        return len(self.nodes)


