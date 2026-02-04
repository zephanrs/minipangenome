# align.py
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import List, Dict, Tuple
from .graph import Graph
from .seed import Seed

MATCH    =  3
MISMATCH = -2
GAP      = -3

@dataclass
class Edit:
  qpos: int
  node: str
  npos: int
  op:   str # M X I D

@dataclass
class Aligner:
  graph: Graph
  preds: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
  succs: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
  topo:  List[str] = field(default_factory=list)

  def __post_init__(self):
    self.build_edges()
    self.toposort()

  def build_edges(self):
    for handle, neighbors in self.graph.edges.items():
      for neighbor in neighbors:
        self.preds[neighbor.node].append(handle.node)
        self.succs[handle.node].append(neighbor.node)

  def toposort(self):
    unvisited = [name for name in self.graph.nodes.keys()]
    visiting = set()

    def visit(node):
      if node in visiting:
        raise ValueError("Graph not a DAG")
      if node not in unvisited:
        return
      unvisited.remove(node)
      visiting.add(node)
      for neighbor in self.succs[node]:
        visit(neighbor)
      visiting.remove(node)
      self.topo.insert(0, node)

    while unvisited:
      visit(unvisited[0])

  def nodes_between(self, start: str, end: str) -> List[str]:
    i_start = self.topo.index(start)
    i_end   = self.topo.index(end)

    allowed = list(self.topo[i_start:i_end+1])
    fwd   = {start}
    queue = deque([start])

    while queue:
      u = queue.popleft()
      for v in self.succs.get(u, []):
        if v in allowed and v not in fwd:
          fwd.add(v)
          queue.append(v)

    bwd   = {end}
    queue = deque([end])

    while queue:
      u = queue.popleft()
      for v in self.preds.get(u, []):
        if v in allowed and v not in bwd:
          bwd.add(v)
          queue.append(v)
        
    mid = fwd & bwd
    if not mid: raise ValueError("no paths between seeds")
    return mid

  def align(self, query: str, chain: List[Seed]) -> List[Edit]:
    active = set(self.preds.get(chain[0].node, []) + self.succs.get(chain[-1].node, []))
    for u, v in zip(chain, chain[1:]):
      active |= set(self.nodes_between(u.node, v.node))
    nodes = [n for n in self.topo if n in active]

    # dp table: (qpos, (node, npos)) -> (score, prev_qpos, prev_state, op)
    dp = {}

    # initialize (query can start anywhere)
    for node in nodes:
      seq = self.graph.nodes[node]
      for npos in range(len(seq)):
        sub, op = (MATCH, 'M') if query[0] == seq[npos] else (MISMATCH, 'X')
        dp[(0, (node, npos))] = (sub, -1, -1, op)

    # compute dp matrix
    for qpos in range(1, len(query)):
      qbase = query[qpos]
      for node in nodes:
        seq = self.graph.nodes[node]
        for npos, base in enumerate(seq):
          state = (node, npos)
          best  = None

          prevs = ([(node, npos - 1)] if npos > 0 else [(p, len(self.graph.nodes[p])-1) 
                   for p in self.preds.get(node, []) if p in active])
          
          # candidates
          candidates = []

          # match / mismatch
          sub, op = (MATCH, 'M') if qbase == base else (MISMATCH, 'X')
          candidates += [(qpos-1, prev, sub, op) for prev in prevs]

          # insertion (graph gap)
          candidates.append((qpos-1, state, GAP, 'I'))

          # deletion (gap in query)
          candidates += [(qpos, prev, GAP, 'D') for prev in prevs]

          # update best candidate
          for prevq, prevs, delta, op in candidates:
            key = (prevq, prevs)
            if key in dp:
              score = dp[key][0] + delta
              if best is None or score > best[0]:
                best = (score, prevq, prevs, op)

          if best is not None:
            dp[(qpos, state)] = best

    # backtracking
    ptr = max((k for k in dp if k[0] == len(query)-1), key=lambda k: dp[k][0])

    edits = []
    while ptr[0] != -1:
      _, prevq, prevs, op = dp[ptr]
      qpos, (node, npos) = ptr
      edits.append(Edit(qpos, node, npos, op))
      ptr = (prevq, prevs)

    edits.reverse()
    return edits
