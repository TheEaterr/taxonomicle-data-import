import networkx as nx
from time import time
import matplotlib.pyplot as plt
from utils import getAndPrintStats, removeAndReconnect

if __name__ == "__main__":
    t = time()
    full_animalia_tree = nx.read_graphml("results/animalia_tree.graphml")
    print(time() - t)
    print("Full tree of animalia (with subspecies) : ", full_animalia_tree)

    # fixing ranks
    full_animalia_tree.nodes["Q107394682"]["rank"] = "genus"
    full_animalia_tree.nodes["Q104857768"]["rank"] = "species"
    full_animalia_tree.nodes["Q104857767"]["rank"] = "species"
    full_animalia_tree.nodes["Q104815681"]["rank"] = "genus"
    full_animalia_tree.nodes["Q117291954"]["rank"] = "genus"
    full_animalia_tree.nodes["Q47966"].pop("rank")
    full_animalia_tree.nodes["Q47969"].pop("rank")
    full_animalia_tree.nodes["Q245695"].pop("rank")
    full_animalia_tree.nodes["Q1085980"].pop("rank")
    full_animalia_tree.nodes["Q1209254"].pop("rank")
    full_animalia_tree.nodes["Q7444798"].pop("rank")
    full_animalia_tree.nodes["Q1096960"].pop("rank")
    full_animalia_tree.nodes["Q2910821"].pop("rank")
    full_animalia_tree.nodes["Q161095"]["rank"] = "infraphylum"
    full_animalia_tree.nodes["Q275544"]["rank"] = "subclass"
    full_animalia_tree.nodes["Q567567"]["rank"] = "superorder"
    full_animalia_tree.nodes["Q205712"]["rank"] = "class"
    full_animalia_tree.nodes["Q10432880"]["rank"] = "suborder"
    full_animalia_tree.nodes["Q17166"]["rank"] = "suborder"
    full_animalia_tree.nodes["Q85762296"]["rank"] = "superfamily"
    full_animalia_tree.nodes["Q95498523"]["rank"] = "family"
    full_animalia_tree.nodes["Q2552226"]["rank"] = "subspecies"
    full_animalia_tree.nodes["Q7181301"]["rank"] = "subspecies"
    full_animalia_tree.nodes["Q113959354"]["rank"] = "species"
    full_animalia_tree.nodes["Q603237"]["rank"] = "subclass"
    full_animalia_tree.nodes["Q160"]["rank"] = "infraorder"
    full_animalia_tree.nodes["Q168366"]["rank"] = "pavorder"
    full_animalia_tree.nodes["Q2781884"].pop("rank")
    full_animalia_tree.nodes["Q85763751"].pop("rank")
    full_animalia_tree.nodes["Q134665"].pop("rank")
    full_animalia_tree.nodes["Q138259"].pop("rank")
    full_animalia_tree.nodes["Q111752876"].pop("rank")
    full_animalia_tree.nodes["Q1633496"].pop("rank")
    full_animalia_tree.nodes["Q160830"].pop("rank")
    full_animalia_tree.nodes["Q2330918"].pop("rank")
    full_animalia_tree.nodes["Q2254408"].pop("rank")
    full_animalia_tree.remove_edge("Q3699922", "Q5158096")
    full_animalia_tree.add_edge("Q1072243", "Q5158096")
    full_animalia_tree.remove_edge("Q3175675", "Q55000290")
    full_animalia_tree.add_edge("Q7415384", "Q55000290")
    full_animalia_tree.remove_edge("Q3175675", "Q55000007")
    full_animalia_tree.add_edge("Q7415384", "Q55000007")
    full_animalia_tree.remove_edge("Q771067", "Q6525920")
    full_animalia_tree.add_edge("Q134759", "Q6525920")
    full_animalia_tree.remove_edge("Q16948752", "Q7253962")
    full_animalia_tree.add_edge("Q3655255", "Q7253962")
    full_animalia_tree.remove_edge("Q18593286", "Q20889393")
    full_animalia_tree.add_edge("Q29877020", "Q20889393")
    full_animalia_tree.remove_edge("Q33144235", "Q35083222")
    full_animalia_tree.add_edge("Q18710482", "Q35083222")
    full_animalia_tree.nodes["Q7253962"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q65076322"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q3055723"]["rank"] = "infraorder"
    full_animalia_tree.nodes["Q10492551"]["rank"] = "subgenus"
    
    def isNotSubspecies(node):
        return full_animalia_tree.nodes[node].get("rank") != "subspecies"

    animalia_tree = nx.subgraph_view(full_animalia_tree, filter_node=isNotSubspecies)

    getAndPrintStats(animalia_tree)
    pruned_animalia_tree = removeAndReconnect(animalia_tree)
    nx.write_graphml_lxml(pruned_animalia_tree, "results/animalia_tree_filtered.graphml")
