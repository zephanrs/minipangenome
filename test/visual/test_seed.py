import os
from pangenome.graph import gfa2graph
from pangenome.seed import Seeder
from pangenome.filter import Filterer
from pangenome.align import Aligner
from pangenome.visualize import graph2png, seeds2png, align2png, alignment_strings

# load graph
gfa_path = os.path.join(os.path.dirname(__file__), "data.gfa")
graph = gfa2graph(gfa_path)
print(f"Graph loaded: {len(graph.nodes)} nodes.")
graph2png(graph, "graph")

query = "GATTACATCCAGT"
k = 3
w = 5
reward = 10

# build seeder + generate seeds
seeder = Seeder(graph, k=k, w=w)
seeds = seeder.seed(query)
print(f"Found {len(seeds)} seeds.")
seeds2png(graph, query, seeds, k, "seeds")

# build filterer + generate chain
filterer = Filterer(graph, type="max", reward=reward, dists={})
chain = filterer.filter(seeds)
print(f"Found a chain of {len(chain)} seeds.")
seeds2png(graph, query, chain, k, "chain")

# 3. alignment
aligner = Aligner(graph)
edits = aligner.align(query, chain)
print(f"Alignment length: {len(edits)} edits.")
align2png(graph, query, edits, "alignment")

q_aln, r_aln = alignment_strings(graph, query, edits)
print("query:     ", q_aln)
print("reference: ", r_aln)