import networkx as nx
import matplotlib.pyplot as plt
from utils import TAXON_RANKS, getAndPrintStats

def analyzeGraph(tree: nx.DiGraph):
    out_degrees = []
    neighbour_diffs = []

    for node in tree.nodes():
        node_rank = tree.nodes[node]["rank"]
        out_degree = tree.out_degree(node)
        if (out_degree > 20) and TAXON_RANKS[node_rank] < TAXON_RANKS["genus"]:
            out_degrees.append(out_degree)
            if (out_degree > 100):
                print("Node ", node, " has out degree ", out_degree)
        # successors = list(tree.successors(node))
        # for successor in successors:
        #     successor_rank = tree.nodes[successor]["rank"]
        #     diff = TAXON_RANKS[successor_rank] - TAXON_RANKS[node_rank]
        #     neighbour_diffs.append(diff)

        #     if diff > 25:
        #         print(f"Node {node} ({node_rank}) has successor {successor} ({successor_rank}) with diff {diff}")

    print("Max diff : ", max(neighbour_diffs))
    # plt.hist(neighbour_diffs, bins=100)
    # plt.title("Neighbour differences")
    # plt.savefig("results/neighbour_diffs.pdf")
    # plt.close()
    plt.hist(out_degrees, bins=100)
    plt.title("Important out degrees")
    plt.savefig("results/out_degrees.pdf")
    plt.close()
    print("Out degree : ", max(out_degrees))

if __name__ == "__main__":
    animalia_tree = nx.read_graphml("results/animalia_tree_filtered.graphml")

    print("Pruned tree of animalia : ", animalia_tree)
    getAndPrintStats(animalia_tree)
    analyzeGraph(animalia_tree)