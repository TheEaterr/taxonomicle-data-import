import networkx as nx
from time import time

if __name__ == "__main__":
    t = time()
    animalia_tree = nx.read_graphml("results/animalia_tree.graphml")
    print(time() - t)
    print(animalia_tree)