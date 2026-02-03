from dataclasses import dataclass, field
from typing import List, Dict, Set
from collections import defaultdict
import graphviz

### Graph Construction

@dataclass(eq=True, frozen=True)
class Handle:
  node: str
  rev:  bool

@dataclass
class Graph:
  nodes: Dict[str, str] = field(default_factory=dict)
  edges: Dict[Handle, Set[Handle]] = field(default_factory=lambda: defaultdict(set))
  paths: Dict[str, List[Handle]] = field(default_factory=dict)

  def add_node(self, id: str, seq: str):
    self.nodes[id] = seq

  def add_edge(self, src: Handle, dst: Handle):
    self.edges[src].add(dst)

  def add_path(self, name: str, path: List[Handle]):
    self.paths[name] = path

### GFA Reading
def gfa2graph(file_path: str):
  graph = Graph()
  with open(file_path, 'r') as file:
    for line in file:
      if line[0] in ['#', 'H'] or not line: continue
      components = line.split('\t')
      match components[0]:
        case "S": graph.add_node(components[1], components[2])
        
        case "L": graph.add_edge(
          Handle(components[1], (components[2] == '-')),
          Handle(components[3], (components[4] == '-'))
        )
        
        case "P": graph.add_path(
          components[1],
          (Handle(node[:-2], (node[-1] == '-')) for node in components[2].split(","))
        )
        
        case _: raise ValueError("Unsupported")
    
  return graph

### Visualization
def graph2png(graph: Graph, name: str):
  # setup
  dot = graphviz.Digraph(filename=name, engine='dot', format='png')
  dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.8')
  dot.attr('node', shape='box', fontname='Helvetica', style='filled', fillcolor='white')
  dot.attr(dpi='300')

  # add nodes
  for id, seq in graph.nodes.items():
    label = seq if len(seq) < 10 else f"{seq[:7]}..."
    dot.node(id, label=label)
  
  # add edges
  for src, dsts in graph.edges.items():
    for dst in dsts:
      srcp = "w" if src.rev else "e"
      dstp = "e" if dst.rev else "w"
      dot.edge(f"{src.node}:{srcp}", f"{dst.node}:{dstp}", color="black")

  # export
  dot.render(cleanup=True)