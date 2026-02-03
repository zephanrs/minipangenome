# seed.py
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict, deque
from graph import Graph
from hash import hash

@dataclass(eq=True, frozen=True)
class Occ:
  node: str
  pos: int
  kmer: str

@dataclass(eq=True, frozen=True)
class Seed:
  qpos: int
  node: str
  npos: int

@dataclass
class Seed:
  graph: Graph
  k: int
  w: int
  index: Dict[int, List[Occ]] = field(init=False)

  def __post_init__(self):
    self.index = self.build_index()

  def build_index(self) -> Dict[int, List[Occ]]:
    index = defaultdict(list)
    for node, seq in self.graph.nodes.items():
      for pos, value in self.minimizers(seq):
        index[value].append(Occ(node, pos, seq[pos:pos + self.k]))
    return dict(index)
  
  def minimizers(self, seq: str):
    values = hash(seq, self.k)
    if not values: return []

    window = min(self.w, len(values))
    positions = deque(range(window))
    minpos = min(positions, key=lambda i: values[i])
    out = [(minpos, values[minpos])]

    for i in range(window, len(values)):
      positions.append(i)

      if minpos == positions.popleft():
        minpos = min(positions, key=lambda i: values[i])
        out.append((minpos, values[minpos]))
      elif values[i] < values[minpos]:
        minpos = i
        out.append((minpos, values[minpos]))
      
    return out

  def get_seeds(self, query: str) -> List[Seed]:
    out = []
    for qpos, value in self.minimizers(query):
      for occ in self.index.get(value, ()):
        if occ.kmer == query[qpos:qpos + self.k]:
          out.append(Seed(qpos, occ.node, occ.pos))
    return out
