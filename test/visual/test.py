import os
from pangenome.graph import gfa2graph, graph2png

gfa_path = os.path.join(os.path.dirname(__file__), "data.gfa")

graph = gfa2graph(gfa_path)
print(f"Graph loaded: {len(graph.nodes)} nodes.")

graph2png(graph, "test_graph")