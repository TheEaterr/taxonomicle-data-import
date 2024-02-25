import networkx as nx
from utils import getAndPrintStats

if __name__ == "__main__":
    animalia_tree = nx.read_graphml("results/animalia_tree_filtered.graphml")

    print("Pruned tree of animalia : ", animalia_tree)
    getAndPrintStats(animalia_tree)