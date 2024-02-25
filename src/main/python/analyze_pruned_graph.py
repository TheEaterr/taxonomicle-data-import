import networkx as nx
import matplotlib.pyplot as plt
from utils import TAXON_RANKS, getAndPrintStats, recurseRemoveNode

def detectNonImageParents(tree: nx.DiGraph):
    for node in tree.nodes():
        if tree.nodes[node].get("image") and tree.nodes[node].get("rank") == "species":
            tree.nodes[node]["image_path"] = True
    changed = True
    while changed:
        changed = False
        for node in tree.nodes():
            if not tree.nodes[node].get("image_path"):
                successors = list(tree.successors(node))
                for successor in successors:
                    if tree.nodes[successor].get("image_path"):
                        tree.nodes[node]["image_path"] = True
                        changed = True
                        break
        print("Ran a loop")

def analyzeGraph(tree: nx.DiGraph):
    out_degrees = []
    neighbour_diffs = []

    for node in tree.nodes():
        node_rank = tree.nodes[node]["rank"]
        successors = list(tree.successors(node))
        real_out_degree = 0
        for successor in successors:
            successor_rank = tree.nodes[successor]["rank"]
            diff = TAXON_RANKS[successor_rank] - TAXON_RANKS[node_rank]
            if diff > 25:
                neighbour_diffs.append(diff)
                print(f"Node {node} ({node_rank}) has successor {successor} ({successor_rank}) with diff {diff}")
                continue

            if TAXON_RANKS[successor_rank] < TAXON_RANKS["species"]:
                real_out_degree += 1

        if real_out_degree > 20 and TAXON_RANKS[node_rank] < TAXON_RANKS["genus"]:
            out_degrees.append(real_out_degree)
            # print("Node ", node, " has out degree ", real_out_degree)

    # print("Max diff : ", max(neighbour_diffs))
    # plt.hist(neighbour_diffs, bins=100)
    # plt.title("Important neighbour differences")
    # plt.savefig("results/neighbour_diffs.pdf")
    # plt.close()
    plt.hist(out_degrees, bins=100)
    plt.title("Important out degrees")
    plt.savefig("results/out_degrees.pdf")
    plt.close()
    print("Out degree : ", max(out_degrees))

def removeImportantDiffs(tree: nx.DiGraph):
    to_remove = []
    nodes = list(tree)[:]
    count = 0
    for node in nodes:
        if tree.nodes().get(node):
            node_rank = tree.nodes[node]["rank"]
            successors = list(tree.successors(node))
            for successor in successors:
                successor_rank = tree.nodes[successor]["rank"]
                diff = TAXON_RANKS[successor_rank] - TAXON_RANKS[node_rank]
                if diff > 25:
                    count = recurseRemoveNode(tree, successor, count)
    print(count)


if __name__ == "__main__":
    animalia_tree = nx.read_graphml("results/animalia_tree_filtered.graphml")

    print("Pruned tree of animalia : ", animalia_tree)
    getAndPrintStats(animalia_tree)
    detectNonImageParents(animalia_tree)

    def isImageParent(node):
        return animalia_tree.nodes[node].get("image_path") == True

    image_animalia_tree = nx.subgraph_view(animalia_tree, filter_node=isImageParent)
    print("Pruned tree of animalia going to images : ", image_animalia_tree)
    getAndPrintStats(image_animalia_tree)

    removeImportantDiffs(animalia_tree)
    print(animalia_tree)
    analyzeGraph(animalia_tree)
    # nx.write_graphml_lxml(animalia_tree, "results/animalia_tree_analyzed.graphml")