import networkx as nx
import json

if __name__ == "__main__":
    animalia_tree = nx.read_graphml("results/animalia_tree_analyzed.graphml")

    data = {}
    data["Q729"] = {}
    for key in animalia_tree.nodes["Q729"]:
        data["Q729"][key] = animalia_tree.nodes["Q729"][key]
    for parent, succs in nx.bfs_successors(animalia_tree, "Q729"):
        for succ in succs:
            data[succ] = {}
            node = animalia_tree.nodes[succ]
            for key in node:
                data[succ][key] = node[key]
                data[succ]["parent"] = parent

    with open("results/animalia_tree.json", "w") as f:
        json.dump(data, f, indent=2)
