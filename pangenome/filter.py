# filter.py
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict, deque
from graph import Graph, Handle

@dataclass
class Filter:
  graph: Graph
  type: str # 'mean' or 'max'
  edges: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(set))
  dists: Dict[str, int] = field(init=False)

  def __post_init__(self):
    self.edges = self.find_edges()
    self.dists = self.linearize()

  def find_edges(self):
    for handle, neighbors in self.graph.edges:
      self.edges[handle.node].extend([neighbor.node for neighbor in neighbors])

  def linearize(self) -> Dict[str, int]:
    dists = {}
    topological = self.toposort()
    costs: defaultdict[str, list[int]] = defaultdict(list)
    costs[topological[0]].append(0)
    for node in topological:
      dists[node] = max(costs[node]) if self.type == 'max' else sum(costs[node]) / len(costs[node])
      for neighbor in self.edges[node]:
        costs[neighbor].append(dists[node] + len(self.graph.nodes[node]))
    return dists
  
  def toposort(self) -> List[str]:
    sorted = []
    visited = [0] * len(self.graph.nodes)
    nodes = self.graph.nodes

    def visit(idx):
      visited[idx] = 1
      node = nodes[idx]
      for neighbor in self.edges[node]:
        visit(nodes.index(neighbor))
      sorted.insert(0, node)

    while not all(visited):
      visit(visited.index(0))

    return sorted
